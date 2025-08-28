# TODO - Fixes for FeedPro Application

## Issues Fixed:

### 1. ✅ Fix "Aditivo y Otros" confusion in ingredient types (not nutrients)
- **Problem**: The confusion was about ingredient types, not nutrient types
- **Solution**: Added "Aditivo" and "Otros" to ingredient types dropdown in alphabetical order
- **Files edited**: 
  - `templates/operaciones/nuevo_ingrediente.html` ✅
  - `templates/operaciones/editar_ingrediente.html` ✅

### 2. ✅ Fix alphabetical ordering for ingredients and nutrients
- **Problem**: Lists were not showing in alphabetical order
- **Solution**: Added `ORDER BY nombre ASC` to all ingredient and nutrient queries
- **Files edited**: 
  - `app/routes/ingredientes.py` ✅ (added ORDER BY to ver_ingredientes)
  - `app/routes/optimizacion.py` ✅ (added ORDER BY to both ingredients and nutrients queries)
  - `app/routes/nutrientes.py` ✅ (already had ORDER BY, cleaned up duplicate code)

### 3. ✅ Fix favicon inconsistency in login page
- **Problem**: Login page used `favicon.ico` but should use `Favicon.png` like other pages
- **Solution**: Changed favicon references to use `Favicon.png`
- **Files edited**: 
  - `templates/sitio/login.html` ✅

### 4. ✅ Fix "Configuracion Personal" title styling
- **Problem**: Title didn't match the rest of the application styling
- **Solution**: Applied same styling as other section titles with icon and proper CSS classes
- **Files edited**: 
  - `templates/operaciones/opciones.html` ✅ (added formulador-header styling and CSS)

### 5. ⏳ Update GitHub after all changes
- **Status**: Ready to commit and push changes

## Summary of Changes Made:

1. **Favicon Fix**: Updated login page to use consistent `Favicon.png` instead of `favicon.ico`
2. **Ingredient Types**: Added "Aditivo" and "Otros" options in alphabetical order to both new and edit ingredient forms
3. **Alphabetical Ordering**: Added `ORDER BY nombre ASC` to ingredient and nutrient queries in routes
4. **Title Styling**: Applied consistent header styling to "Configuración Personal" section
5. **Code Cleanup**: Removed duplicate code in nutrientes.py

## Next Step:
- Commit and push all changes to GitHub repository

## Technical Details:

### Ingredient Types Available (Alphabetical):
1. Aditivo
2. Aminoácido
3. Energía
4. Fibra
5. Mineral
6. Otros
7. Proteína
8. Vitamina

### Database Changes:
- No schema changes required
- Ordering handled at query level with ORDER BY
- New ingredient types validated at application level

### Files Modified:
- `templates/sitio/login.html` - Favicon consistency
- `templates/operaciones/nuevo_ingrediente.html` - Added ingredient types
- `templates/operaciones/editar_ingrediente.html` - Added ingredient types  
- `templates/operaciones/opciones.html` - Header styling
- `app/routes/ingredientes.py` - Alphabetical ordering
- `app/routes/optimizacion.py` - Alphabetical ordering
- `app/routes/nutrientes.py` - Code cleanup
