---
name: excel-wizard
description: Excel formula reference, VBA macros, data cleaning, and chart guidance
---

# Excel Wizard

## When to Use
User asks about Excel formulas, VBA, data manipulation, charts, or spreadsheet tasks. User has Microsoft Excel OAuth2 credential for API access.

## Formula Quick Reference

**Lookups:**
- `VLOOKUP(value, range, col, FALSE)` -- exact match lookup (legacy)
- `INDEX(range, MATCH(value, lookup_range, 0))` -- preferred, more flexible
- `XLOOKUP(value, lookup, return, "Not Found")` -- modern, use when available

**Conditional aggregation:**
- `SUMIFS(sum_range, criteria_range1, criteria1, ...)` -- sum with multiple conditions
- `COUNTIFS(range1, criteria1, ...)` -- count with conditions
- `AVERAGEIFS(avg_range, range1, criteria1, ...)` -- average with conditions

**Text:**
- `TEXTJOIN(",", TRUE, range)` -- join with delimiter, skip blanks
- `LEFT/RIGHT/MID(text, n)` -- extract characters
- `TRIM(CLEAN(cell))` -- remove whitespace and non-printable chars

**Dates:**
- `NETWORKDAYS(start, end)` -- business days between dates
- `EOMONTH(date, 0)` -- end of current month
- `TEXT(date, "YYYY-MM-DD")` -- format date as text

**Arrays (365/Online):**
- `UNIQUE(range)` -- deduplicate
- `SORT(range, col, order)` -- dynamic sort
- `FILTER(range, criteria)` -- dynamic filter

## Pivot Table Setup
1. Select data range (ensure headers in row 1)
2. Insert > PivotTable
3. Drag fields: Rows = categories, Values = numbers (Sum/Count), Columns = secondary grouping
4. Right-click values > Value Field Settings to change aggregation

## Data Cleaning Checklist
1. Remove duplicates: Data > Remove Duplicates
2. Trim spaces: `=TRIM(A1)` then paste values
3. Fix dates: `=DATEVALUE(TEXT(A1,"YYYY-MM-DD"))`
4. Find blanks: Ctrl+G > Special > Blanks
5. Standardize text: `=PROPER(TRIM(A1))` or `=UPPER()`
6. Remove non-printable: `=CLEAN(A1)`

## Chart Selection
| Data Type | Chart |
|-----------|-------|
| Compare categories | Bar/Column |
| Trend over time | Line |
| Part of whole | Pie (max 6 slices) or Stacked Bar |
| Correlation | Scatter |
| Distribution | Histogram |
| Multiple metrics | Combo (bar + line) |

## VBA Quick Templates

**Loop through rows:**
```vba
Sub ProcessRows()
    Dim ws As Worksheet: Set ws = ActiveSheet
    Dim lastRow As Long: lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    Dim i As Long
    For i = 2 To lastRow
        ' Process ws.Cells(i, 1).Value
    Next i
End Sub
```

**Auto-format table:**
```vba
Sub FormatTable()
    With Range("A1").CurrentRegion
        .Borders.LineStyle = xlContinuous
        .Rows(1).Font.Bold = True
        .Rows(1).Interior.Color = RGB(0, 112, 192)
        .Rows(1).Font.Color = vbWhite
        .Columns.AutoFit
    End With
End Sub
```

## Keyboard Shortcuts
- `Ctrl+T` -- create table
- `Ctrl+Shift+L` -- toggle filters
- `Alt+=` -- auto-sum
- `Ctrl+;` -- insert today's date
- `F4` -- toggle absolute reference ($)
- `Ctrl+` ` -- show formulas
