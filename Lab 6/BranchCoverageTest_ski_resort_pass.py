import unittest
from ski_resort_pass import process_resort_bookings, check_chairlift_anemometer


class TestSkiResortBranchCoverage(unittest.TestCase):
    """
    Focused on achieving 100% Branch Coverage (--branch).
    Tests both True and False outcomes of every conditional and loop in ski_resort_pass.py.
    """

    def test_invalid_inputs_both_conditions(self):
        # Condition 1: not isinstance(groups, list) is True
        with self.assertRaises(ValueError):
            process_resort_bookings(None, 15.0)
        # Condition 2: isinstance(groups, list) is True, facility_fee < 0 is True
        with self.assertRaises(ValueError):
            process_resort_bookings([], -10.0)

    def test_empty_and_inactive_groups_zero_sales(self):
        # Empty groups list -> loop 0 iterations -> ZERO_SALES
        self.assertEqual(
            process_resort_bookings([], 15.0),
            {"total_revenue": 0.0, "status": "ZERO_SALES"}
        )
        # Inactive group -> is_active False branch -> ZERO_SALES
        groups = [{"is_active": False, "duration": "full_day", "skiers": [{"age": 25}]}]
        self.assertEqual(
            process_resort_bookings(groups, 15.0),
            {"total_revenue": 0.0, "status": "ZERO_SALES"}
        )

    def test_all_durations_and_skier_branches_completed(self):
        groups = [
            # 1. Invalid duration -> else branch (rejected_passes = 1)
            {
                "is_active": True,
                "duration": "invalid_type",
                "skiers": [{"age": 25}]
            },
            # 2. Season pass with lodge locker (includes_lodge_locker = True)
            # Covers: age <= 0 (True), blackout_override (True) with duration != "half_day" (False),
            # age < 12 (True), age >= 65 (True), adult else, and gear_rental (True & False)
            {
                "is_active": True,
                "duration": "season",
                "includes_lodge_locker": True,
                "skiers": [
                    {"age": 0},  # rejected_passes = 2
                    {"age": 25, "blackout_override": True, "gear_rental": True},  # rejected = 3; 150 + 35 = 185
                    {"age": 8, "gear_rental": False},   # Child without gear: 180
                    {"age": 68, "gear_rental": True},   # Senior with gear: 210 + 35 = 245
                    {"age": 35, "gear_rental": False},  # Adult without gear: 300
                ]
            },
            # 3. Full-day pass without lodge locker (includes_lodge_locker = False)
            {
                "is_active": True,
                "duration": "full_day",
                "includes_lodge_locker": False,
                "skiers": [
                    {"age": 30, "gear_rental": False}  # 80
                ]
            },
            # 4. Half-day pass without blackout_override (completes skier loop normally)
            {
                "is_active": True,
                "duration": "half_day",
                "includes_lodge_locker": False,
                "skiers": [
                    {"age": 22, "blackout_override": False, "gear_rental": False}  # 50
                ]
            },
            # 5. Half-day pass with blackout_override (triggers pass_duration == "half_day" True & break)
            {
                "is_active": True,
                "duration": "half_day",
                "includes_lodge_locker": False,
                "skiers": [
                    {"age": 22, "blackout_override": True, "gear_rental": True}  # rejected = 4; resets to 0 & breaks
                ]
            }
        ]
        # Total = (185 + 180 + 245 + 300 + 25) + 80 + 50 + 0 = 1065.0
        result = process_resort_bookings(groups, 25.0)
        self.assertEqual(result, {"total_revenue": 1065.0, "status": "COMPLETED"})

    def test_audit_review_branch(self):
        # Covers rejected_passes > 4 True branch
        groups = [
            {
                "is_active": True,
                "duration": "full_day",
                "skiers": [
                    {"age": 0},
                    {"age": -2},
                    {"age": 0},
                    {"age": -1},
                    {"age": 0},
                    {"age": 30}
                ]
            }
        ]
        result = process_resort_bookings(groups, 10.0)
        self.assertEqual(result, {"total_revenue": 80.0, "status": "AUDIT_REVIEW"})

    def test_anemometer_all_branches(self):
        # 1. wind_streams empty -> True branch ("NO_DATA")
        self.assertEqual(check_chairlift_anemometer([]), "NO_DATA")

        # 2. speed_mph > 45 twice in a row -> wind_gust_streak >= 2 True ("SUSPEND_LIFT")
        self.assertEqual(
            check_chairlift_anemometer([[46, 48]]),
            "SUSPEND_LIFT"
        )

        # 3. Single gust > 45 (wind_gust_streak >= 2 False) followed by <= 45 reset -> "SAFE_OPERATION"
        self.assertEqual(
            check_chairlift_anemometer([[], [47, 30, 46, 20]]),
            "SAFE_OPERATION"
        )


if __name__ == "__main__":
    unittest.main()