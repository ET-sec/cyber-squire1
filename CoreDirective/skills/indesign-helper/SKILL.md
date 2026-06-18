---
name: indesign-helper
description: IDML generation rules, JSX scripting reference, and InDesign automation
---

# InDesign Helper

## When to Use
User asks about InDesign, IDML files, ExtendScript/JSX, or print layout automation.

## IDML Generation - Critical Rules

These are HARD REQUIREMENTS. Violating any will produce broken files:

1. **designmap.xml MUST reference every story:**
   ```xml
   <idPkg:Story src="Stories/Story_u123.xml"/>
   ```
   Without this, InDesign shows empty frames even if story XML exists in the ZIP.

2. **BackingStory reference required:**
   ```xml
   <idPkg:BackingStory src="XML/BackingStory.xml"/>
   ```

3. **TextFrame transparency:**
   ```xml
   <TextFrame FillColor="Swatch/None" ...>
   ```
   Without `FillColor="Swatch/None"`, frames obscure content behind them.

4. **Remove ALL old refs before adding new ones.** Duplicate or orphaned refs in designmap.xml cause import errors for MasterSpread, Spread, Story, and BackingStory elements.

## IDML File Structure
```
document.idml (ZIP)
├── designmap.xml          # Master manifest - refs everything
├── META-INF/container.xml
├── Resources/
│   ├── Fonts.xml
│   ├── Graphic.xml
│   ├── Preferences.xml
│   └── Styles.xml
├── MasterSpreads/
│   └── MasterSpread_*.xml
├── Spreads/
│   └── Spread_*.xml       # Page layouts with TextFrame/Rectangle refs
├── Stories/
│   └── Story_*.xml        # Text content
├── XML/
│   ├── BackingStory.xml
│   └── Tags.xml
└── Mapping.xml
```

## Common JSX Operations

**Place image:**
```javascript
var frame = app.activeDocument.pages[0].rectangles.add();
frame.geometricBounds = [y1, x1, y2, x2]; // [top, left, bottom, right] in points
frame.place(File("/path/to/image.jpg"));
frame.fit(FitOptions.PROPORTIONALLY);
```

**Flow text into frame:**
```javascript
var tf = app.activeDocument.pages[0].textFrames.add();
tf.geometricBounds = [36, 36, 756, 540];
tf.contents = "Your text here";
tf.texts[0].appliedParagraphStyle = app.activeDocument.paragraphStyles.itemByName("Body");
```

**Create master page:**
```javascript
var master = app.activeDocument.masterSpreads.add();
master.name = "B-Content";
master.baseName = "B";
```

**Export PDF:**
```javascript
app.activeDocument.exportFile(ExportFormat.PDF_TYPE, File("~/Desktop/output.pdf"), false, app.pdfExportPresets.itemByName("[High Quality Print]"));
```

## ExtendScript Debugging
- Use `$.writeln()` for console output in ESTK
- `try/catch` everything -- InDesign errors are cryptic
- Test with `app.scriptPreferences.enableRedraw = false` for speed
- Always `app.doScript(function(){...}, ScriptLanguage.JAVASCRIPT, undefined, UndoModes.ENTIRE_SCRIPT)` for undo support
