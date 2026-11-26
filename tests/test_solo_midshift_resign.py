from linebeads.retrocheck_slots.midshift import reconcile_shift, resign_shift, resign_table


def _board():
    return [
        {'key': 'A', 'cohort': '甲区', 'state': '已分派', 'cost': 2, 'revision': 1, 'estimate': 40},
        {'key': 'B', 'cohort': '甲区', 'state': '候补', 'cost': 1, 'revision': 1, 'estimate': 35},
        {'key': 'C', 'cohort': '乙区', 'state': '候补', 'cost': 1, 'revision': 1, 'estimate': 35},
    ]


def test_withdrawal_only_backfills_same_zone_un_departed_waitlist():
    result = resign_shift(_board(), [{'key': 'A', 'revision': 2, 'estimate': 5}], capacity=3)
    assert result.by_key('A').action == '撤回'
    assert result.by_key('B').action == '补派'
    assert result.by_key('C').action == '保留'
    assert result.reconciliation['balanced']
    assert reconcile_shift(result)


def test_departed_ordinary_reading_is_locked():
    board = [
        {'key': 'A', 'cohort': '甲区', 'state': '已分派', 'cost': 1, 'departed': True, 'estimate': 40},
        {'key': 'B', 'cohort': '甲区', 'state': '候补', 'cost': 1, 'estimate': 35},
    ]
    result = resign_shift(board, [{'key': 'A', 'revision': 2, 'estimate': 1}], capacity=2)
    assert result.by_key('A').action == '保留'
    assert result.by_key('A').locked is True
    assert result.by_key('B').action != '补派'


def test_wet_reading_overrides_departed_lock_and_recomputes():
    board = [
        {'key': 'A', 'cohort': '甲区', 'state': '已分派', 'cost': 1, 'departed': True},
        {'key': 'B', 'cohort': '甲区', 'state': '候补', 'cost': 1},
    ]
    result = resign_shift(board, [{'key': 'A', 'revision': 2, 'retro_cd': 110, 'wet_pct': 78}], capacity=2)
    assert result.by_key('A').action == '暂停'
    assert result.by_key('A').occupied == 0
    assert result.by_key('B').action == '补派'
    assert result.reconciliation['balanced']


def test_reordered_and_duplicated_batch_do_not_change_table():
    revisions = [
        {'key': 'A', 'revision': 2, 'estimate': 5},
        {'key': 'C', 'revision': 2, 'retro_cd': 100, 'wet_pct': 80},
    ]
    board = _board() + [{'key': 'D', 'cohort': '乙区', 'state': '已分派', 'cost': 1}]
    first = resign_table(board, revisions, capacity=4)
    reordered = resign_table(board, list(reversed(revisions)), capacity=4)
    repeated = resign_table(board, revisions + [dict(item) for item in revisions], capacity=4)
    assert first == reordered
    assert first == repeated
    assert first.result.reconciliation['balanced']
