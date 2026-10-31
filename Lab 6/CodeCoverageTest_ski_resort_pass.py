import unittest
from ski_resort_pass import process_resort_bookings, check_chairlift_anemometer


class TestSkiResortCodeCoverage(unittest.TestCase):
    """
    Focused on achieving >=90% (100%) Line/Statement Coverage.
    Executes every line in ski_resort_pass.py without testing every
    alternate True/False branch outcome (e.g., skips non-half_day blackout
    override and non-rental gear path).
    """

    def test_invalid_input_raises_error(self):
        with self.assertRaises(ValueError):
            process_resort_bookings("invalid_groups", 20.0)

    def test_zero_sales_inactive_group(self):
        groups = [{"is_active": False, "duration": "season", "skiers": [{"age": 25}]}]
        self.assertEqual(
            process_resort_bookings(groups, 20.0),
            {"total_revenue": 0.0, "status": "ZERO_SALES"}
        )

    def test_bookings_line_coverage(self):
        groups = [
            # Invalid duration line
            {"is_active": True, "duration": "weekly", "skiers": []},
            # Season pass with child, senior, adult, invalid age, gear rental, and locker
            {
                "is_active": True,
                "duration": "season",
                "includes_lodge_locker": True,
                "skiers": [
                    {"age": 0},  # age <= 0
                    {"age": 25, "blackout_override": True, "gear_rental": True},  # blackout on season
                    {"age": 10, "gear_rental": True},  # age < 12
                    {"age": 70, "gear_rental": True},  # age >= 65
                    {"age": 30, "gear_rental": True},  # adult else branch
                ]
            },
            # Full day pass
            {
                "is_active": True,
                "duration": "full_day",
                "includes_lodge_locker": True,
                "skiers": [{"age": 30, "gear_rental": True}]
            },
            # Half day pass with blackout override (triggers break)
            {
                "is_active": True,
                "duration": "half_day",
                "includes_lodge_locker": True,
                "skiers": [{"age": 25, "blackout_override": True}]
            }
        ]
        result = process_resort_bookings(groups, 25.0)
        self.assertEqual(result["status"], "COMPLETED")

    def test_audit_review_status(self):
        groups = [
            {
                "is_active": True,
                "duration": "full_day",
                "includes_lodge_locker": True,
                "skiers": [{"age": -1}, {"age": -1}, {"age": -1}, {"age": -1}, {"age": -1}]
            }
        ]
        result = process_resort_bookings(groups, 10.0)
        self.assertEqual(result["status"], "AUDIT_REVIEW")

    def test_anemometer_line_coverage(self):
        self.assertEqual(check_chairlift_anemometer([]), "NO_DATA")
        self.assertEqual(check_chairlift_anemometer([[30, 48, 50]]), "SUSPEND_LIFT")
        self.assertEqual(check_chairlift_anemometer([[30, 40]]), "SAFE_OPERATION")


if __name__ == "__main__":
    unittest.main()