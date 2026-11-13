# Decision Log — ECE-042

| ID | Decision | Reason |
|---|---|---|
| D-01 | Use Python and CSV files | The project brief permits a CLI/file-driven implementation. |
| D-02 | Use Decimal for money | Avoid binary floating-point rounding errors in currency calculations. |
| D-03 | Include the exact 24-hour return boundary | The brief says within 24 hours; the boundary is explicitly included. |
| D-04 | Exactly 120 seconds is not a duplicate | The duplicate rule is strictly less than two minutes. |
| D-05 | Duplicate key is tag ID plus lane | Duplicate detection is lane-specific. |
| D-06 | Equal-time order is PASS, RECHARGE, READ | Follows the supplied sample-pack tie-break rule. |
| D-07 | Higher detected class incurs ₹100 penalty | Implements the class-mismatch rule. |
| D-08 | Lower detected class is ignored | Registered class remains authoritative when detection is lower. |
| D-09 | Exemption takes priority over mismatch | Exempt tags are logged at zero charge; mismatch is not applied to exempt tags. |
| D-10 | Pass fare coverage does not waive mismatch penalty | The pass covers toll fare; the mismatch penalty remains payable. |
| D-11 | Pass purchase is separate cash collection | It does not reduce the prepaid tag balance. |
| D-12 | A tag is unblacklisted only above zero balance | A zero balance does not satisfy the positive-balance recovery condition. |
| D-13 | A new successful pass purchase replaces the previous active pass | One active pass is maintained per tag in this single-plaza model. |
| D-14 | Return history tracks paid toll crossings | Pass-covered and exempt crossings do not establish a paid return-trip history. |
| D-15 | Generated output CSVs are excluded from Git | Keeps the repository focused on source, tests and documentation. |

## Items to confirm with mentor

The brief does not fully specify every interaction. Confirm whether the ₹100 mismatch penalty should be charged from the prepaid balance when a pass covers the toll, and whether an exempt tag with a higher detected class should be flagged for re-verification. This implementation records the decisions above consistently.
