#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.checkers.checking import CheckPluginName

REPLACED_CHECK_PLUGINS = {
    CheckPluginName("aix_diskiod"): CheckPluginName("diskstat_io"),
    CheckPluginName("apc_symmetra_power"): CheckPluginName("epower"),
    CheckPluginName("cisco_mem_asa"): CheckPluginName("cisco_mem"),
    CheckPluginName("cisco_mem_asa64"): CheckPluginName("cisco_mem"),
    CheckPluginName("df_netapp32"): CheckPluginName("df_netapp"),
    CheckPluginName("emc_vplex_volumes"): CheckPluginName("diskstat_io_volumes"),
    CheckPluginName("emc_vplex_director_stats"): CheckPluginName("diskstat_io_director"),
    CheckPluginName("fjdarye100_cadaps"): CheckPluginName("fjdarye_channel_adapters"),
    CheckPluginName("fjdarye100_cmods"): CheckPluginName("fjdarye_channel_modules"),
    CheckPluginName("fjdarye100_cmods_mem"): CheckPluginName("fjdarye_controller_modules_memory"),
    CheckPluginName("fjdarye100_conencs"): CheckPluginName("fjdarye_controller_enclosures"),
    CheckPluginName("fjdarye100_cpsus"): CheckPluginName("fjdarye_ce_power_supply_units"),
    CheckPluginName("fjdarye100_devencs"): CheckPluginName("fjdarye_device_enclosures"),
    CheckPluginName("fjdarye100_disks"): CheckPluginName("fjdarye_disks"),
    CheckPluginName("fjdarye100_disks_summary"): CheckPluginName("fjdarye_disks_summary"),
    CheckPluginName("fjdarye100_rluns"): CheckPluginName("fjdarye_rluns"),
    CheckPluginName("fjdarye100_sum"): CheckPluginName("fjdarye_summary_status"),
    CheckPluginName("fjdarye100_syscaps"): CheckPluginName("fjdarye_system_capacitors"),
    CheckPluginName("fjdarye101_cadaps"): CheckPluginName("fjdarye_channel_adapters"),
    CheckPluginName("fjdarye101_cmods"): CheckPluginName("fjdarye_channel_modules"),
    CheckPluginName("fjdarye101_cmods_mem"): CheckPluginName("fjdarye_controller_modules_memory"),
    CheckPluginName("fjdarye101_conencs"): CheckPluginName("fjdarye_controller_enclosures"),
    CheckPluginName("fjdarye101_devencs"): CheckPluginName("fjdarye_device_enclosures"),
    CheckPluginName("fjdarye101_disks"): CheckPluginName("fjdarye_disks"),
    CheckPluginName("fjdarye101_disks_summary"): CheckPluginName("fjdarye_disks_summary"),
    CheckPluginName("fjdarye101_rluns"): CheckPluginName("fjdarye_rluns"),
    CheckPluginName("fjdarye101_sum"): CheckPluginName("fjdarye_summary_status"),
    CheckPluginName("fjdarye101_syscaps"): CheckPluginName("fjdarye_system_capacitors"),
    CheckPluginName("fjdarye200_pools"): CheckPluginName("fjdarye_pools"),
    CheckPluginName("fjdarye500_cadaps"): CheckPluginName("fjdarye_channel_adapters"),
    CheckPluginName("fjdarye500_ca_ports"): CheckPluginName("fjdarye_ca_ports"),
    CheckPluginName("fjdarye500_cmods"): CheckPluginName("fjdarye_channel_modules"),
    CheckPluginName("fjdarye500_cmods_flash"): CheckPluginName("fjdarye_controller_modules_flash"),
    CheckPluginName("fjdarye500_cmods_mem"): CheckPluginName("fjdarye_controller_modules_memory"),
    CheckPluginName("fjdarye500_conencs"): CheckPluginName("fjdarye_controller_enclosures"),
    CheckPluginName("fjdarye500_cpsus"): CheckPluginName("fjdarye_ce_power_supply_units"),
    CheckPluginName("fjdarye500_devencs"): CheckPluginName("fjdarye_device_enclosures"),
    CheckPluginName("fjdarye500_disks"): CheckPluginName("fjdarye_disks"),
    CheckPluginName("fjdarye500_disks_summary"): CheckPluginName("fjdarye_disks_summary"),
    CheckPluginName("fjdarye500_expanders"): CheckPluginName("fjdarye_expanders"),
    CheckPluginName("fjdarye500_inletthmls"): CheckPluginName("fjdarye_inlet_thermal_sensors"),
    CheckPluginName("fjdarye500_pfm"): CheckPluginName("fjdarye_pcie_flash_modules"),
    CheckPluginName("fjdarye500_sum"): CheckPluginName("fjdarye_summary_status"),
    CheckPluginName("fjdarye500_syscaps"): CheckPluginName("fjdarye_system_capacitors"),
    CheckPluginName("fjdarye500_thmls"): CheckPluginName("fjdarye_thermal_sensors"),
    CheckPluginName("fjdarye60_cadaps"): CheckPluginName("fjdarye_channel_adapters"),
    CheckPluginName("fjdarye60_cmods"): CheckPluginName("fjdarye_channel_modules"),
    CheckPluginName("fjdarye60_cmods_flash"): CheckPluginName("fjdarye_controller_modules_flash"),
    CheckPluginName("fjdarye60_cmods_mem"): CheckPluginName("fjdarye_controller_modules_memory"),
    CheckPluginName("fjdarye60_conencs"): CheckPluginName("fjdarye_controller_enclosures"),
    CheckPluginName("fjdarye60_devencs"): CheckPluginName("fjdarye_device_enclosures"),
    CheckPluginName("fjdarye60_disks"): CheckPluginName("fjdarye_disks"),
    CheckPluginName("fjdarye60_disks_summary"): CheckPluginName("fjdarye_disks_summary"),
    CheckPluginName("fjdarye60_expanders"): CheckPluginName("fjdarye_expanders"),
    CheckPluginName("fjdarye60_inletthmls"): CheckPluginName("fjdarye_inlet_thermal_sensors"),
    CheckPluginName("fjdarye60_psus"): CheckPluginName("fjdarye_power_supply_units"),
    CheckPluginName("fjdarye60_rluns"): CheckPluginName("fjdarye_rluns"),
    CheckPluginName("fjdarye60_sum"): CheckPluginName("fjdarye_summary_status"),
    CheckPluginName("fjdarye60_syscaps"): CheckPluginName("fjdarye_system_capacitors"),
    CheckPluginName("fjdarye60_thmls"): CheckPluginName("fjdarye_thermal_sensors"),
    CheckPluginName("hpux_lunstats"): CheckPluginName("diskstat_io"),
    CheckPluginName("jolokia_metrics_uptime"): CheckPluginName("jolokia_jvm_runtime"),
    CheckPluginName("jolokia_metrics_gc"): CheckPluginName("jolokia_jvm_garbagecollectors"),
    CheckPluginName("ups_power"): CheckPluginName("epower"),
    CheckPluginName("esx_vsphere_counters"): CheckPluginName("esx_vsphere_datastore_io"),
    CheckPluginName("arista_bgp"): CheckPluginName("bgp_peer"),
}
