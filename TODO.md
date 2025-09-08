# TODO: Pricing Plans and Module Changes

## ✅ Completed Tasks
- [x] Analysis of current implementation
- [x] Plan creation and approval
- [x] Update `templates/sitio/precios.html` - Show only 3 plans (Básico, Avanzado, Institucional)
- [x] Update `templates/sitio/formulario_cobro.html` - Update plan selection options
- [x] Rename "Personal" to "Avanzado" throughout the system
- [x] Update `app/routes/auth.py` - Modify test users and plan assignments
- [x] Update `app/routes/usuarios.py` - Update plan management logic
- [x] Update `templates/operaciones/administrador.html` - Update admin interface
- [x] Update `templates/operaciones/panel.html` - Remove reports module access
- [x] Update `templates/operaciones/layout.html` - Remove reports from navigation
- [x] Update `templates/operaciones/opciones.html` - Update plan descriptions

## 🔄 In Progress Tasks

## 📋 Pending Tasks

### 4. Update Plan Access Controls
- [x] Verify Herramientas module has comparative reports functionality
- [x] Update plan-based access controls in templates
- [ ] Test new plan structure

### 5. Testing and Verification
- [ ] Test pricing page displays correctly
- [ ] Test plan selection in forms
- [ ] Test user authentication with new plans
- [ ] Test admin interface with new plan structure
- [ ] Verify comparative reports work in Herramientas

## 📝 Notes
- Básico: 30 formulas limit, 50 ingredients limit
- Avanzado (previously Personal): unlimited formulas and ingredients, personalized advisory, access to all tools
- Institucional: remains the same
- Profesional: hidden temporarily
- Reporte Comparativo: moved to Herramientas (already implemented)
- Generador de Reportes: access removed from panels

## 🎯 Summary of Changes Made
1. **Pricing Structure**: Updated to show only 3 plans (Básico, Avanzado, Institucional)
2. **Plan Renaming**: Changed "Personal" to "Avanzado" throughout the system
3. **Professional Plan**: Hidden temporarily from all interfaces
4. **Reports Module**: Removed "Generador de Reportes" access from panels
5. **Comparative Reports**: Functionality remains available in Herramientas module
6. **Authentication**: Updated test users to reflect new plan structure
7. **Admin Interface**: Updated plan options and descriptions
8. **Navigation**: Cleaned up menus to remove reports module access
9. **User Options**: Updated plan descriptions and badges
