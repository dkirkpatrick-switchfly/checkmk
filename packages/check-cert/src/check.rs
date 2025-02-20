// Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
// This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
// conditions defined in the file COPYING, which is part of this source code package.

use std::fmt::{Display, Formatter, Result as FormatResult};
use std::mem;
use typed_builder::TypedBuilder;

#[derive(Debug, Clone)]
pub enum Real {
    Integer(isize),
    Double(f64),
}

impl Default for Real {
    fn default() -> Self {
        Self::Integer(isize::default())
    }
}

impl From<isize> for Real {
    fn from(x: isize) -> Self {
        Real::Integer(x)
    }
}

impl From<f64> for Real {
    fn from(x: f64) -> Self {
        Real::Double(x)
    }
}

impl Display for Real {
    fn fmt(&self, f: &mut Formatter) -> FormatResult {
        match self {
            Self::Integer(x) => write!(f, "{}", x),
            Self::Double(x) => write!(f, "{:.06}", x),
        }
    }
}

#[derive(Debug, Clone)]
#[cfg_attr(test, derive(PartialEq))]
pub struct Bounds<T>
where
    T: Clone,
{
    pub min: T,
    pub max: T,
}

impl<T> Bounds<T>
where
    T: Clone,
{
    pub fn map<F, U>(self, f: F) -> Bounds<U>
    where
        F: FnMut(T) -> U,
        U: Clone + Default,
    {
        Bounds::from(&mut [self.min, self.max].map(f))
    }
}

impl<T> From<&mut [T; 2]> for Bounds<T>
where
    T: Clone + Default,
{
    fn from(arr: &mut [T; 2]) -> Self {
        Self {
            min: mem::take(&mut arr[0]),
            max: mem::take(&mut arr[1]),
        }
    }
}

#[derive(Debug, Clone)]
#[cfg_attr(test, derive(PartialEq))]
pub struct Levels<T> {
    pub warn: T,
    pub crit: T,
}

impl<T> Levels<T>
where
    T: Clone,
{
    pub fn map<F, U>(self, f: F) -> Levels<U>
    where
        F: FnMut(T) -> U,
        U: Clone + Default,
    {
        Levels::from(&mut [self.warn, self.crit].map(f))
    }
}

impl<T> From<&mut [T; 2]> for Levels<T>
where
    T: Default,
{
    fn from(arr: &mut [T; 2]) -> Self {
        Self {
            warn: mem::take(&mut arr[0]),
            crit: mem::take(&mut arr[1]),
        }
    }
}

#[derive(Debug)]
pub enum LevelsStrategy {
    Upper,
    Lower,
}

impl LevelsStrategy {
    pub fn cmp<T: PartialOrd>(&self, x: &T, y: &T) -> bool {
        match self {
            Self::Upper => PartialOrd::ge(x, y),
            Self::Lower => PartialOrd::lt(x, y),
        }
    }
}

#[derive(Debug, TypedBuilder)]
pub struct LevelsCheckerArgs {
    #[builder(setter(transform = |x: impl Into<String>| x.into() ))]
    label: String,
    #[builder(default, setter(transform = |x: impl Into<String>| Some(x.into()) ))]
    uom: Option<String>,
}

#[derive(Debug)]
pub struct LevelsChecker<T> {
    strategy: LevelsStrategy,
    levels: Levels<T>,
}

impl<T> LevelsChecker<T>
where
    T: Clone + PartialOrd,
{
    pub fn try_new(
        strategy: LevelsStrategy,
        levels: Levels<T>,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        strategy
            .cmp(&levels.crit, &levels.warn)
            .then_some(Self { strategy, levels })
            .ok_or(Box::from("bad values"))
    }

    pub fn check(
        &self,
        value: T,
        summary: impl Into<String>,
        args: LevelsCheckerArgs,
    ) -> CheckResult<T> {
        let evaluate = |value: &T| -> State {
            if self.strategy.cmp(value, &self.levels.crit) {
                State::Crit
            } else if self.strategy.cmp(value, &self.levels.warn) {
                State::Warn
            } else {
                State::Ok
            }
        };
        let r = SimpleCheckResult::new(evaluate(&value), summary);
        CheckResult {
            summary: r.summary,
            metrics: Some(Metric::<T> {
                label: args.label,
                value,
                uom: args.uom,
                levels: Some(self.levels.clone()),
                bounds: None,
            }),
        }
    }
}

#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
enum State {
    #[default]
    Ok,
    Warn,
    Crit,
    Unknown,
}

impl State {
    fn as_str(&self) -> &'static str {
        match self {
            Self::Ok => "OK",
            Self::Warn => "WARNING",
            Self::Crit => "CRITICAL",
            Self::Unknown => "UNKNOWN",
        }
    }
}

#[derive(Debug, Default, Clone, TypedBuilder)]
#[cfg_attr(test, derive(PartialEq))]
pub struct Metric<T>
where
    T: Clone,
{
    #[builder(setter(transform = |x: impl Into<String>| x.into() ))]
    label: String,
    value: T,
    #[builder(default, setter(transform = |x: impl Into<String>| Some(x.into()) ))]
    uom: Option<String>,
    #[builder(default, setter(strip_option))]
    levels: Option<Levels<T>>,
    #[builder(default, setter(strip_option))]
    bounds: Option<Bounds<T>>,
}

impl<T> Metric<T>
where
    T: Clone,
{
    pub fn map<F, U>(self, mut f: F) -> Metric<U>
    where
        F: FnMut(T) -> U,
        F: Copy,
        U: Clone + Default,
    {
        Metric {
            label: self.label,
            value: f(self.value),
            uom: self.uom,
            levels: self.levels.map(|v| v.map(f)),
            bounds: self.bounds.map(|v| v.map(f)),
        }
    }
}

impl<T> Display for Metric<T>
where
    T: Clone + Display,
{
    fn fmt(&self, f: &mut Formatter) -> FormatResult {
        write!(
            f,
            "{}={}{};{};{};{};{}",
            self.label,
            self.value,
            self.uom.clone().unwrap_or_default(),
            self.levels
                .as_ref()
                .map_or(String::new(), |v| v.warn.to_string()),
            self.levels
                .as_ref()
                .map_or(String::new(), |v| v.crit.to_string()),
            self.bounds
                .as_ref()
                .map_or(String::new(), |v| v.min.to_string()),
            self.bounds
                .as_ref()
                .map_or(String::new(), |v| v.max.to_string()),
        )
    }
}

#[derive(Debug, Default, Clone)]
pub struct Summary {
    state: State,
    text: String,
}

impl Summary {
    fn new(state: State, text: impl Into<String>) -> Self {
        Self {
            state,
            text: text.into(),
        }
    }
}

impl Display for Summary {
    fn fmt(&self, f: &mut Formatter<'_>) -> FormatResult {
        write!(
            f,
            "{}{}",
            self.text,
            match self.state {
                State::Ok => "",
                State::Warn => " (!)",
                State::Crit => " (!!)",
                State::Unknown => " (?)",
            }
        )
    }
}

#[derive(Debug, Default)]
pub struct SimpleCheckResult {
    summary: Summary,
}

impl SimpleCheckResult {
    fn new(state: State, text: impl Into<String>) -> Self {
        Self {
            summary: Summary::new(state, text),
        }
    }

    pub fn ok(summary: impl Into<String>) -> Self {
        Self::new(State::Ok, summary)
    }

    pub fn warn(summary: impl Into<String>) -> Self {
        Self::new(State::Warn, summary)
    }

    pub fn crit(summary: impl Into<String>) -> Self {
        Self::new(State::Crit, summary)
    }

    pub fn unknown(summary: impl Into<String>) -> Self {
        Self::new(State::Unknown, summary)
    }
}

pub struct CheckResult<T>
where
    T: Clone,
{
    summary: Summary,
    metrics: Option<Metric<T>>,
}

impl<T> Default for CheckResult<T>
where
    T: Clone,
{
    fn default() -> Self {
        SimpleCheckResult::default().into()
    }
}

impl<T> CheckResult<T>
where
    T: Clone,
{
    fn new(state: State, text: impl Into<String>, metrics: Option<Metric<T>>) -> Self {
        Self {
            summary: Summary::new(state, text),
            metrics,
        }
    }

    pub fn ok(summary: impl Into<String>, metrics: Metric<T>) -> Self {
        Self::new(State::Ok, summary, Some(metrics))
    }

    pub fn warn(summary: impl Into<String>, metrics: Metric<T>) -> Self {
        Self::new(State::Warn, summary, Some(metrics))
    }

    pub fn crit(summary: impl Into<String>, metrics: Metric<T>) -> Self {
        Self::new(State::Crit, summary, Some(metrics))
    }

    pub fn unknown(summary: impl Into<String>, metrics: Metric<T>) -> Self {
        Self::new(State::Unknown, summary, Some(metrics))
    }
}

impl<T> CheckResult<T>
where
    T: Clone,
{
    pub fn map<F, U>(self, f: F) -> CheckResult<U>
    where
        F: FnMut(T) -> U,
        F: Copy,
        U: Clone + Default,
    {
        CheckResult {
            summary: self.summary,
            metrics: self.metrics.map(|m| m.map(f)),
        }
    }
}

impl<T> From<SimpleCheckResult> for CheckResult<T>
where
    T: Clone,
{
    fn from(x: SimpleCheckResult) -> Self {
        Self {
            summary: x.summary,
            metrics: None,
        }
    }
}

#[derive(Debug, Default)]
pub struct Collection {
    state: State,
    summary: Vec<Summary>,
    metrics: Vec<Metric<Real>>,
}

impl Collection {
    pub fn join(&mut self, other: &mut Collection) {
        self.state = std::cmp::max(self.state, other.state);
        self.summary.append(&mut other.summary);
        self.metrics.append(&mut other.metrics);
    }
}

impl Display for Collection {
    fn fmt(&self, f: &mut Formatter) -> FormatResult {
        let mut out = String::from(self.state.as_str());
        let summary = self
            .summary
            .iter()
            .filter(|s| !s.text.is_empty())
            .map(ToString::to_string)
            .collect::<Vec<_>>()
            .join(", ");
        if !summary.is_empty() {
            out = format!("{} - {}", out, summary);
        }
        let metrics = self
            .metrics
            .iter()
            .map(ToString::to_string)
            .collect::<Vec<_>>()
            .join(", ");
        if !metrics.is_empty() {
            out = format!("{} | {}", out, metrics);
        }
        write!(f, "{}", out)?;
        Ok(())
    }
}

impl From<SimpleCheckResult> for Collection {
    fn from(check_result: SimpleCheckResult) -> Self {
        Self {
            state: check_result.summary.state,
            summary: vec![check_result.summary],
            metrics: Vec::<Metric<Real>>::default(),
        }
    }
}

impl From<&mut Vec<CheckResult<Real>>> for Collection {
    fn from(check_results: &mut Vec<CheckResult<Real>>) -> Self {
        check_results
            .drain(..)
            .fold(Collection::default(), |mut out, cr| {
                out.state = std::cmp::max(out.state, cr.summary.state);
                out.summary.push(cr.summary);
                out.metrics.extend(cr.metrics);
                out
            })
    }
}

pub fn exit_code(collection: &Collection) -> i32 {
    match collection.state {
        State::Ok => 0,
        State::Warn => 1,
        State::Crit => 2,
        State::Unknown => 3,
    }
}

pub fn bail_out(message: impl Into<String>) -> ! {
    let out = Collection::from(SimpleCheckResult::unknown(message));
    println!("{}", out);
    std::process::exit(exit_code(&out))
}

pub fn abort(message: impl Into<String>) -> ! {
    let out = Collection::from(SimpleCheckResult::crit(message));
    println!("{}", out);
    std::process::exit(exit_code(&out))
}

#[cfg(test)]
mod test_metrics_map {
    use super::{Bounds, Levels, Metric};

    #[test]
    fn test_bounds() {
        assert_eq!(
            Bounds { min: 1, max: 10 }.map(&|v| v * 10),
            Bounds { min: 10, max: 100 }
        );
        assert_eq!(
            Bounds::from(&mut [1, 10]).map(&|v| v * 10),
            Bounds { min: 10, max: 100 }
        );
    }

    #[test]
    fn test_levels() {
        assert_eq!(
            Levels { warn: 1, crit: 10 }.map(&|v| v * 10),
            Levels {
                warn: 10,
                crit: 100
            }
        );
        assert_eq!(
            Levels::from(&mut [1, 10]).map(&|v| v * 10),
            Levels {
                warn: 10,
                crit: 100,
            }
        );
    }

    #[test]
    fn test_metric() {
        assert_eq!(
            Metric::builder()
                .label("Label")
                .value(42)
                .uom("unit")
                .levels(Levels { warn: 5, crit: 10 })
                .bounds(Bounds { min: 1, max: 10 })
                .build()
                .map(|v| v * 10),
            Metric::builder()
                .label("Label")
                .value(420)
                .uom("unit")
                .levels(Levels {
                    warn: 50,
                    crit: 100,
                })
                .bounds(Bounds { min: 10, max: 100 })
                .build()
        );
    }
}

#[cfg(test)]
mod test_metrics_display {
    use super::{Bounds, Levels, Metric, Real};

    fn i(x: isize) -> Real {
        Real::Integer(x)
    }

    fn d(x: f64) -> Real {
        Real::Double(x)
    }

    #[test]
    fn test_default() {
        assert_eq!(
            format!(
                "{}",
                Metric::<Real>::builder().label("name").value(i(42)).build()
            ),
            "name=42;;;;"
        );
    }

    #[test]
    fn test_uom() {
        assert_eq!(
            format!(
                "{}",
                Metric::<Real>::builder()
                    .label("name")
                    .value(i(42))
                    .uom("ms")
                    .build()
            ),
            "name=42ms;;;;"
        );
    }

    #[test]
    fn test_levels() {
        assert_eq!(
            format!(
                "{}",
                Metric::<Real>::builder()
                    .label("name")
                    .value(i(42))
                    .levels(Levels {
                        warn: i(24),
                        crit: i(42)
                    })
                    .build()
            ),
            "name=42;24;42;;"
        );
    }

    #[test]
    fn test_chain_all_integer() {
        assert_eq!(
            format!(
                "{}",
                Metric::<Real>::builder()
                    .label("name")
                    .value(i(42))
                    .uom("ms")
                    .levels(Levels {
                        warn: i(24),
                        crit: i(42)
                    })
                    .bounds(Bounds {
                        min: i(0),
                        max: i(100)
                    })
                    .build()
            ),
            "name=42ms;24;42;0;100"
        );
    }

    #[test]
    fn test_chain_all_double() {
        assert_eq!(
            format!(
                "{}",
                Metric::<Real>::builder()
                    .label("name")
                    .value(d(42.0))
                    .uom("ms")
                    .levels(Levels {
                        warn: d(24.0),
                        crit: d(42.0)
                    })
                    .bounds(Bounds {
                        min: d(0.0),
                        max: d(100.0)
                    })
                    .build()
            ),
            "name=42.000000ms;24.000000;42.000000;0.000000;100.000000"
        );
    }
}

#[cfg(test)]
mod test_writer_format {
    use super::{CheckResult, Collection, Metric, Real, SimpleCheckResult};

    #[test]
    fn test_single_check_result_ok() {
        assert_eq!(
            format!("{}", Collection::from(SimpleCheckResult::ok("summary"))),
            "OK - summary"
        );
    }

    #[test]
    fn test_single_check_result_warn() {
        assert_eq!(
            format!("{}", Collection::from(SimpleCheckResult::warn("summary"))),
            "WARNING - summary (!)"
        );
    }

    #[test]
    fn test_single_check_result_crit() {
        assert_eq!(
            format!("{}", Collection::from(SimpleCheckResult::crit("summary"))),
            "CRITICAL - summary (!!)"
        );
    }

    #[test]
    fn test_single_check_result_unknown() {
        assert_eq!(
            format!(
                "{}",
                Collection::from(SimpleCheckResult::unknown("summary"))
            ),
            "UNKNOWN - summary (?)"
        );
    }

    #[test]
    fn test_no_check_results_is_ok() {
        assert_eq!(format!("{}", Collection::from(&mut vec![])), "OK");
    }

    #[test]
    fn test_merge_check_results_with_state_only() {
        let cr1 = SimpleCheckResult::default();
        let cr2 = SimpleCheckResult::default();
        let cr3 = SimpleCheckResult::default();
        assert_eq!(
            format!(
                "{}",
                Collection::from(&mut vec![cr1.into(), cr2.into(), cr3.into()])
            ),
            "OK"
        );
    }

    #[test]
    fn test_merge_check_results_ok() {
        let cr1 = SimpleCheckResult::ok("summary 1");
        let cr2 = SimpleCheckResult::ok("summary 2");
        let cr3 = SimpleCheckResult::ok("summary 3");
        assert_eq!(
            format!(
                "{}",
                Collection::from(&mut vec![cr1.into(), cr2.into(), cr3.into()])
            ),
            "OK - summary 1, summary 2, summary 3"
        );
    }

    #[test]
    fn test_merge_check_results_warn() {
        let cr1 = SimpleCheckResult::ok("summary 1");
        let cr2 = SimpleCheckResult::warn("summary 2");
        let cr3 = SimpleCheckResult::ok("summary 3");
        assert_eq!(
            format!(
                "{}",
                Collection::from(&mut vec![cr1.into(), cr2.into(), cr3.into()])
            ),
            "WARNING - summary 1, summary 2 (!), summary 3"
        );
    }

    #[test]
    fn test_merge_check_results_crit() {
        let cr1 = SimpleCheckResult::ok("summary 1");
        let cr2 = SimpleCheckResult::warn("summary 2");
        let cr3 = SimpleCheckResult::crit("summary 3");
        assert_eq!(
            format!(
                "{}",
                Collection::from(&mut vec![cr1.into(), cr2.into(), cr3.into()])
            ),
            "CRITICAL - summary 1, summary 2 (!), summary 3 (!!)"
        );
    }

    #[test]
    fn test_merge_check_results_unknown() {
        let cr1 = SimpleCheckResult::ok("summary 1");
        let cr2 = SimpleCheckResult::warn("summary 2");
        let cr3 = SimpleCheckResult::crit("summary 3");
        let cr4 = SimpleCheckResult::unknown("summary 4");
        assert_eq!(
            format!(
                "{}",
                Collection::from(&mut vec![cr1.into(), cr2.into(), cr3.into(), cr4.into()])
            ),
            "UNKNOWN - summary 1, summary 2 (!), summary 3 (!!), summary 4 (?)"
        );
    }

    fn m(name: &str, x: isize) -> Metric<Real> {
        Metric::<Real>::builder()
            .label(name)
            .value(Real::Integer(x))
            .build()
    }

    #[test]
    fn test_merge_check_results_with_metrics() {
        let cr1 = CheckResult::ok("summary 1", m("m1", 13));
        let cr2 = CheckResult::warn("summary 2", m("m2", 37));
        let cr3 = CheckResult::crit("summary 3", m("m3", 42));
        let mut vec = vec![cr1, cr2, cr3];
        assert_eq!(
            format!("{}", Collection::from(&mut vec)),
            "CRITICAL - summary 1, summary 2 (!), summary 3 (!!) \
            | m1=13;;;;, m2=37;;;;, m3=42;;;;"
        );
        assert!(vec.is_empty());
    }

    #[test]
    fn test_join_writers_with_metrics() {
        let mut c = Collection::default();
        c.join(&mut Collection::from(&mut vec![CheckResult::ok(
            "summary 1",
            m("m1", 13),
        )]));
        c.join(&mut Collection::from(&mut vec![CheckResult::warn(
            "summary 2",
            m("m2", 37),
        )]));
        c.join(&mut Collection::from(&mut vec![CheckResult::crit(
            "summary 3",
            m("m3", 42),
        )]));
        assert_eq!(
            format!("{}", c),
            "CRITICAL - summary 1, summary 2 (!), summary 3 (!!) \
            | m1=13;;;;, m2=37;;;;, m3=42;;;;"
        );
    }
}
