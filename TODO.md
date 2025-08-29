# Fix Flask BuildError - Blueprint Reference Issue

## Problem
- Flask BuildError: Could not build url for endpoint 'reportes_bp.reportes'
- Template references old blueprint name but actual registered blueprint is 'reportes_mejorado_bp'
- Error occurs at line 240 in templates/operaciones/layout.html

## Steps to Complete

### ✅ Analysis Complete
- [x] Identified the issue in layout.html line 240
- [x] Confirmed reportes_mejorado_bp is the registered blueprint in app/__init__.py
- [x] Confirmed reportes_bp is not registered

### ✅ Implementation Complete
- [x] Fix blueprint reference in templates/operaciones/layout.html (line 240)
- [x] Search for any other references to old reportes_bp blueprint
- [x] Fix all 3 references in templates/operaciones/panel.html
- [x] Verify no other template files contain reportes_bp references

### ✅ Files Updated
- templates/operaciones/layout.html (1 reference fixed)
- templates/operaciones/panel.html (3 references fixed)

### ✅ Temporary Changes for Presentation
- [x] Hide "Planificador de Producción" from navigation menu
- [x] Hide "Generador de Reportes" from navigation menu
- [x] Hide reportes summary card from panel
- [x] Hide reportes quick action from dropdown
- [x] Hide reportes and planificador nav cards from main panel

### 📋 Files with Temporary Changes
- templates/operaciones/layout.html (navigation menu items commented out)
- templates/operaciones/panel.html (summary cards and nav cards commented out)

## Expected Result
- Flask application loads without BuildError
- Only functional features visible for presentation
- Non-functional features temporarily hidden with comments for easy restoration
