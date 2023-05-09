#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# yapf: disable
# type: ignore

checkname = 'varnish'

info = [[u'client_conn', u'13688122', u'4.41', u'Client', u'connections', u'accepted'],
        [u'client_drop', u'0', u'0.00', u'Connection', u'dropped,', u'no', u'sess/wrk'],
        [u'client_req', u'22399444', u'7.21', u'Client', u'requests', u'received'],
        [u'cache_hit', u'3679', u'0.00', u'Cache', u'hits'],
        [u'cache_hitpass', u'0', u'0.00', u'Cache', u'hits', u'for', u'pass'],
        [u'cache_miss', u'5688', u'0.00', u'Cache', u'misses'],
        [u'backend_conn', u'6870905', u'2.21', u'Backend', u'conn.', u'success'],
        [u'backend_unhealthy', u'0', u'0.00', u'Backend', u'conn.', u'not', u'attempted'],
        [u'backend_busy', u'0', u'0.00', u'Backend', u'conn.', u'too', u'many'],
        [u'backend_fail', u'0', u'0.00', u'Backend', u'conn.', u'failures'],
        [u'backend_reuse', u'15529663', u'5.00', u'Backend', u'conn.', u'reuses'],
        [u'backend_toolate', u'6235', u'0.00', u'Backend', u'conn.', u'was', u'closed'],
        [u'backend_recycle', u'15535904', u'5.00', u'Backend', u'conn.', u'recycles'],
        [u'backend_retry', u'46', u'0.00', u'Backend', u'conn.', u'retry'],
        [u'fetch_head', u'2027', u'0.00', u'Fetch', u'head'],
        [u'fetch_length', u'262229', u'0.08', u'Fetch', u'with', u'Length'],
        [u'fetch_chunked', u'15036092', u'4.84', u'Fetch', u'chunked'],
        [u'fetch_eof', u'0', u'0.00', u'Fetch', u'EOF'],
        [u'fetch_bad', u'0', u'0.00', u'Fetch', u'had', u'bad', u'headers'],
        [u'fetch_close', u'0', u'0.00', u'Fetch', u'wanted', u'close'],
        [u'fetch_oldhttp', u'0', u'0.00', u'Fetch', u'pre', u'HTTP/1.1', u'closed'],
        [u'fetch_zero', u'0', u'0.00', u'Fetch', u'zero', u'len'],
        [u'fetch_failed', u'0', u'0.00', u'Fetch', u'failed'],
        [u'fetch_1xx', u'0', u'0.00', u'Fetch', u'no', u'body', u'(1xx)'],
        [u'fetch_204', u'0', u'0.00', u'Fetch', u'no', u'body', u'(204)'],
        [u'fetch_304', u'242538', u'0.08', u'Fetch', u'no', u'body', u'(304)'],
        [u'n_sess_mem', u'100000', u'.', u'N', u'struct', u'sess_mem'],
        [u'n_sess', u'205478', u'.', u'N', u'struct', u'sess'],
        [u'n_object', u'6', u'.', u'N', u'struct', u'object'],
        [u'n_vampireobject', u'0', u'.', u'N', u'unresurrected', u'objects'],
        [u'n_objectcore', u'103', u'.', u'N', u'struct', u'objectcore'],
        [u'n_objecthead', u'106', u'.', u'N', u'struct', u'objecthead'],
        [u'n_waitinglist', u'1656', u'.', u'N', u'struct', u'waitinglist'],
        [u'n_vbc', u'63', u'.', u'N', u'struct', u'vbc'],
        [u'n_wrk', u'1000', u'.', u'N', u'worker', u'threads'],
        [u'n_wrk_create', u'1000', u'0.00', u'N', u'worker', u'threads', u'created'],
        [u'n_wrk_failed', u'0', u'0.00', u'N', u'worker', u'threads', u'not', u'created'],
        [u'n_wrk_max', u'893', u'0.00', u'N', u'worker', u'threads', u'limited'],
        [u'n_wrk_lqueue', u'0', u'0.00', u'work', u'request', u'queue', u'length'],
        [u'n_wrk_queued', u'21', u'0.00', u'N', u'queued', u'work', u'requests'],
        [u'n_wrk_drop', u'0', u'0.00', u'N', u'dropped', u'work', u'requests'],
        [u'n_backend', u'2', u'.', u'N', u'backends'],
        [u'n_expired', u'5680', u'.', u'N', u'expired', u'objects'],
        [u'n_lru_nuked', u'0', u'.', u'N', u'LRU', u'nuked', u'objects'],
        [u'n_lru_moved', u'1031', u'.', u'N', u'LRU', u'moved', u'objects'],
        [u'losthdr', u'0', u'0.00', u'HTTP', u'header', u'overflows'],
        [u'n_objsendfile', u'0', u'0.00', u'Objects', u'sent', u'with', u'sendfile'],
        [u'n_objwrite', u'15304594', u'4.93', u'Objects', u'sent', u'with', u'write'],
        [u'n_objoverflow', u'0', u'0.00', u'Objects', u'overflowing', u'workspace'],
        [u's_sess', u'13688192', u'4.41', u'Total', u'Sessions'],
        [u's_req', u'22399444', u'7.21', u'Total', u'Requests'],
        [u's_pipe', u'6857383', u'2.21', u'Total', u'pipe'],
        [u's_pass', u'15537563', u'5.00', u'Total', u'pass'],
        [u's_fetch', u'15536463', u'5.00', u'Total', u'fetch'],
        [u's_hdrbytes', u'2623668048', u'844.77', u'Total', u'header', u'bytes'],
        [u's_bodybytes', u'64230617131', u'20680.97', u'Total', u'body', u'bytes'],
        [u'sess_closed', u'13155380', u'4.24', u'Session', u'Closed'],
        [u'sess_pipeline', u'0', u'0.00', u'Session', u'Pipeline'],
        [u'sess_readahead', u'0', u'0.00', u'Session', u'Read', u'Ahead'],
        [u'sess_linger', u'15527441', u'5.00', u'Session', u'Linger'],
        [u'sess_herd', u'14213158', u'4.58', u'Session', u'herd'],
        [u'shm_records', u'1455329990', u'468.59', u'SHM', u'records'],
        [u'shm_writes', u'117704314', u'37.90', u'SHM', u'writes'],
        [u'shm_flushes', u'0', u'0.00', u'SHM', u'flushes', u'due', u'to', u'overflow'],
        [u'shm_cont', u'1081722', u'0.35', u'SHM', u'MTX', u'contention'],
        [u'shm_cycles', u'646', u'0.00', u'SHM', u'cycles', u'through', u'buffer'],
        [u'sms_nreq', u'1919', u'0.00', u'SMS', u'allocator', u'requests'],
        [u'sms_nobj', u'0', u'.', u'SMS', u'outstanding', u'allocations'],
        [u'sms_nbytes', u'0', u'.', u'SMS', u'outstanding', u'bytes'],
        [u'sms_balloc', u'708111', u'.', u'SMS', u'bytes', u'allocated'],
        [u'sms_bfree', u'708111', u'.', u'SMS', u'bytes', u'freed'],
        [u'backend_req', u'15543010', u'5.00', u'Backend', u'requests', u'made'],
        [u'n_vcl', u'1', u'0.00', u'N', u'vcl', u'total'],
        [u'n_vcl_avail', u'1', u'0.00', u'N', u'vcl', u'available'],
        [u'n_vcl_discard', u'0', u'0.00', u'N', u'vcl', u'discarded'],
        [u'n_ban', u'1', u'.', u'N', u'total', u'active', u'bans'],
        [u'n_ban_add', u'1', u'0.00', u'N', u'new', u'bans', u'added'],
        [u'n_ban_retire', u'0', u'0.00', u'N', u'old', u'bans', u'deleted'],
        [u'n_ban_obj_test', u'0', u'0.00', u'N', u'objects', u'tested'],
        [u'n_ban_re_test', u'0', u'0.00', u'N', u'regexps', u'tested', u'against'],
        [u'n_ban_dups', u'0', u'0.00', u'N', u'duplicate', u'bans', u'removed'],
        [u'hcb_nolock', u'9357', u'0.00', u'HCB', u'Lookups', u'without', u'lock'],
        [u'hcb_lock', u'5680', u'0.00', u'HCB', u'Lookups', u'with', u'lock'],
        [u'hcb_insert', u'5536', u'0.00', u'HCB', u'Inserts'],
        [u'esi_errors', u'0', u'0.00', u'ESI', u'parse', u'errors', u'(unlock)'],
        [u'esi_warnings', u'0', u'0.00', u'ESI', u'parse', u'warnings', u'(unlock)'],
        [u'accept_fail', u'0', u'0.00', u'Accept', u'failures'],
        [u'client_drop_late', u'0', u'0.00', u'Connection', u'dropped', u'late'],
        [u'dir_dns_lookups', u'0', u'0.00', u'DNS', u'director', u'lookups'],
        [u'dir_dns_failed', u'0', u'0.00', u'DNS', u'director', u'failed', u'lookups'],
        [u'dir_dns_hit', u'0', u'0.00', u'DNS', u'director', u'cached', u'lookups', u'hit'],
        [u'dir_dns_cache_full', u'0', u'0.00', u'DNS', u'director', u'full', u'dnscache'],
        [u'vmods', u'1', u'.', u'Loaded', u'VMODs'],
        [u'n_gzip', u'0', u'0.00', u'Gzip', u'operations'],
        [u'n_gunzip', u'82397', u'0.03', u'Gunzip', u'operations'],
        [u'LCK.sms.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.sms.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.sms.locks', u'5757', u'0.00', u'Lock', u'Operations'],
        [u'LCK.sms.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.smp.creat', u'0', u'0.00', u'Created', u'locks'],
        [u'LCK.smp.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.smp.locks', u'0', u'0.00', u'Lock', u'Operations'],
        [u'LCK.smp.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.sma.creat', u'2', u'0.00', u'Created', u'locks'],
        [u'LCK.sma.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.sma.locks', u'76789246', u'24.72', u'Lock', u'Operations'],
        [u'LCK.sma.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.smf.creat', u'0', u'0.00', u'Created', u'locks'],
        [u'LCK.smf.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.smf.locks', u'0', u'0.00', u'Lock', u'Operations'],
        [u'LCK.smf.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.hsl.creat', u'0', u'0.00', u'Created', u'locks'],
        [u'LCK.hsl.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.hsl.locks', u'0', u'0.00', u'Lock', u'Operations'],
        [u'LCK.hsl.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.hcb.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.hcb.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.hcb.locks', u'28465', u'0.01', u'Lock', u'Operations'],
        [u'LCK.hcb.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.hcl.creat', u'0', u'0.00', u'Created', u'locks'],
        [u'LCK.hcl.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.hcl.locks', u'0', u'0.00', u'Lock', u'Operations'],
        [u'LCK.hcl.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.vcl.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.vcl.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.vcl.locks', u'2851', u'0.00', u'Lock', u'Operations'],
        [u'LCK.vcl.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.stat.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.stat.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.stat.locks', u'100000', u'0.03', u'Lock', u'Operations'],
        [u'LCK.stat.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.sessmem.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.sessmem.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.sessmem.locks', u'13788830', u'4.44', u'Lock', u'Operations'],
        [u'LCK.sessmem.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.wstat.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.wstat.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.wstat.locks', u'9610420', u'3.09', u'Lock', u'Operations'],
        [u'LCK.wstat.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.herder.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.herder.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.herder.locks', u'1', u'0.00', u'Lock', u'Operations'],
        [u'LCK.herder.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.wq.creat', u'2', u'0.00', u'Created', u'locks'],
        [u'LCK.wq.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.wq.locks', u'60935122', u'19.62', u'Lock', u'Operations'],
        [u'LCK.wq.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.objhdr.creat', u'5630', u'0.00', u'Created', u'locks'],
        [u'LCK.objhdr.destroy', u'5528', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.objhdr.locks', u'50493', u'0.02', u'Lock', u'Operations'],
        [u'LCK.objhdr.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.exp.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.exp.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.exp.locks', u'3116883', u'1.00', u'Lock', u'Operations'],
        [u'LCK.exp.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.lru.creat', u'2', u'0.00', u'Created', u'locks'],
        [u'LCK.lru.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.lru.locks', u'5686', u'0.00', u'Lock', u'Operations'],
        [u'LCK.lru.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.cli.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.cli.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.cli.locks', u'1034607', u'0.33', u'Lock', u'Operations'],
        [u'LCK.cli.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.ban.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.ban.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.ban.locks', u'3116888', u'1.00', u'Lock', u'Operations'],
        [u'LCK.ban.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.vbp.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.vbp.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.vbp.locks', u'0', u'0.00', u'Lock', u'Operations'],
        [u'LCK.vbp.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.vbe.creat', u'1', u'0.00', u'Created', u'locks'],
        [u'LCK.vbe.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.vbe.locks', u'13742087', u'4.42', u'Lock', u'Operations'],
        [u'LCK.vbe.colls', u'0', u'0.00', u'Collisions'],
        [u'LCK.backend.creat', u'2', u'0.00', u'Created', u'locks'],
        [u'LCK.backend.destroy', u'0', u'0.00', u'Destroyed', u'locks'],
        [u'LCK.backend.locks', u'51690378', u'16.64', u'Lock', u'Operations'],
        [u'LCK.backend.colls', u'0', u'0.00', u'Collisions'],
        [u'SMA.s0.c_req', u'13217', u'0.00', u'Allocator', u'requests'],
        [u'SMA.s0.c_fail', u'0', u'0.00', u'Allocator', u'failures'],
        [u'SMA.s0.c_bytes', u'960020137', u'309.11', u'Bytes', u'allocated'],
        [u'SMA.s0.c_freed', u'959606425', u'308.97', u'Bytes', u'freed'],
        [u'SMA.s0.g_alloc', u'14', u'.', u'Allocations', u'outstanding'],
        [u'SMA.s0.g_bytes', u'413712', u'.', u'Bytes', u'outstanding'],
        [u'SMA.s0.g_space', u'268021744', u'.', u'Bytes', u'available'],
        [u'SMA.Transient.c_req', u'30824441', u'9.92', u'Allocator', u'requests'],
        [u'SMA.Transient.c_fail', u'0', u'0.00', u'Allocator', u'failures'],
        [u'SMA.Transient.c_bytes', u'2050011605312', u'660062.73', u'Bytes', u'allocated'],
        [u'SMA.Transient.c_freed', u'2050011605312', u'660062.73', u'Bytes', u'freed'],
        [u'SMA.Transient.g_alloc', u'0', u'.', u'Allocations', u'outstanding'],
        [u'SMA.Transient.g_bytes', u'0', u'.', u'Bytes', u'outstanding'],
        [u'SMA.Transient.g_space', u'0', u'.', u'Bytes', u'available'],
        [u'VBE.default(127.0.0.1,,81).vcls', u'1', u'.', u'VCL', u'references'],
        [u'VBE.default(127.0.0.1,,81).happy', u'0', u'.', u'Happy', u'health', u'probes'],
        [u'VBE.stepstone(X.X.X.X,,80).vcls', u'1', u'.', u'VCL', u'references'],
        [u'VBE.stepstone(X.X.X.X,,80).happy', u'0', u'.', u'Happy', u'health', u'probes']]

discovery = {
    '': [],
    'backend': [(None, {})],
    'backend_success_ratio': [(None, {})],
    'cache': [(None, {})],
    'cache_hit_ratio': [(None, {})],
    'client': [(None, {})],
    'esi': [(None, {})],
    'fetch': [(None, {})],
    'objects': [(None, {})],
    'worker': [(None, {})],
    'worker_thread_ratio': [(None, {})]
}

checks = {
    'backend': [(None, {}, [(0, u'0.0 conn. too many/s',
                             [(u'varnish_backend_busy_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 conn. not attempted/s',
                             [(u'varnish_backend_unhealthy_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 requests made/s',
                             [(u'varnish_backend_req_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 conn. recycles/s',
                             [(u'varnish_backend_recycle_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 conn. retry/s',
                             [(u'varnish_backend_retry_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 conn. failures/s',
                             [(u'varnish_backend_fail_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 conn. was closed/s',
                             [(u'varnish_backend_toolate_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 conn. success/s',
                             [(u'varnish_backend_conn_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 conn. reuses/s',
                             [(u'varnish_backend_reuse_rate', 0.0, None, None, None, None)])])],
    'backend_success_ratio': [(None, {
        'levels_lower': (70.0, 60.0)
    }, [(0, '100%', [('varnish_backend_success_ratio', 100.0, None,
                                                       None, None, None)])])],
    'cache': [(None, {}, [(0, u'0.0 misses/s',
                           [(u'varnish_cache_miss_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 hits/s',
                           [(u'varnish_cache_hit_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 hits for pass/s',
                           [(u'varnish_cache_hitpass_rate', 0.0, None, None, None, None)])])],
    'cache_hit_ratio': [(None, {
        'levels_lower': (70.0, 60.0)
    }, [(2, '39.28% (warn/crit below 70.0%/60.0%)',
         [('cache_hit_ratio', 39.2761823422654, None, None, None, None)])])],
    'client': [(None, {}, [(0, u'0.0 Connection dropped, no sess wrk/s',
                            [(u'varnish_client_drop_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 requests received/s',
                            [(u'varnish_client_req_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 connections accepted/s',
                            [(u'varnish_client_conn_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 Connection dropped late/s',
                            [(u'varnish_client_drop_late_rate', 0.0, None, None, None, None)])])],
    'esi': [(None, {
        'errors': (1.0, 2.0)
    }, [(0, u'0.0 parse errors (unlock)/s', [(u'varnish_esi_errors_rate',
                                                                       0.0, 1.0, 2.0, None, None)]),
        (0, u'0.0 parse warnings (unlock)/s',
         [(u'varnish_esi_warnings_rate', 0.0, None, None, None, None)])])],
    'fetch': [(None, {}, [(0, u'0.0 pre HTTP 1.1 closed/s',
                           [(u'varnish_fetch_oldhttp_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 head/s',
                           [(u'varnish_fetch_head_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 EOF/s',
                           [(u'varnish_fetch_eof_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 zero len/s',
                           [(u'varnish_fetch_zero_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 no body (304)/s',
                           [(u'varnish_fetch_304_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 with Length/s',
                           [(u'varnish_fetch_length_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 failed/s',
                           [(u'varnish_fetch_failed_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 had bad headers/s',
                           [(u'varnish_fetch_bad_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 wanted close/s',
                           [(u'varnish_fetch_close_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 no body (1xx)/s',
                           [(u'varnish_fetch_1xx_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 chunked/s',
                           [(u'varnish_fetch_chunked_rate', 0.0, None, None, None, None)]),
                          (0, u'0.0 no body (204)/s',
                           [(u'varnish_fetch_204_rate', 0.0, None, None, None, None)])])],
    'objects': [(None, {}, [(0, u'0.0 expired objects/s',
                             [(u'varnish_objects_expired_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 LRU nuked objects/s',
                             [(u'varnish_objects_lru_nuked_rate', 0.0, None, None, None, None)]),
                            (0, u'0.0 LRU moved objects/s',
                             [(u'varnish_objects_lru_moved_rate', 0.0, None, None, None, None)])])],
    'worker': [(None, {}, [(0, u'0.0 work request queue length/s',
                            [(u'varnish_worker_lqueue_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 worker threads created/s',
                            [(u'varnish_worker_create_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 dropped work requests/s',
                            [(u'varnish_worker_drop_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 worker threads/s',
                            [(u'varnish_worker_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 worker threads not created/s',
                            [(u'varnish_worker_failed_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 queued work requests/s',
                            [(u'varnish_worker_queued_rate', 0.0, None, None, None, None)]),
                           (0, u'0.0 worker threads limited/s',
                            [(u'varnish_worker_max_rate', 0.0, None, None, None, None)])])],
    'worker_thread_ratio': [(None, {
        'levels_lower': (70.0, 60.0)
    }, [(0, '100%', [('varnish_worker_thread_ratio', 100.0, None,
                                                     None, None, None)])])]
}
