# TODO - Pricing System Testing Implementation

## Plan Overview
Implement proper testing for the three pricing plans with consistent user flow:
- Básico: Only tools
- Personal: Tools + Reports  
- Profesional: Tools + Reports + Production Management

## Tasks to Complete

### 1. Fix Pricing Page (templates/sitio/precios.html)
- [x] Change Básico plan button to use "Empezar prueba gratis" flow instead of direct payment
- [x] Fix Institucional plan "Contactar ventas" button to redirect to form
- [x] Ensure all plans use consistent styling and flow
- [x] Add proper plan parameter passing to form

### 2. Update Form Handler (templates/sitio/formulario_cobro.html)
- [x] Add institutional plan option to the form
- [x] Ensure all plan types are properly handled
- [x] Add custom pricing option for institutional plan
- [x] Update JavaScript to handle all plan types

### 3. Enhance Backend (app/routes/usuarios.py)
- [x] Add institutional plan handling in form processing
- [x] Update email templates for different plan types
- [x] Add proper validation for all plan types
- [x] Ensure payment links work for all plans

### 4. Implement Plan-Based Access Control
- [x] Check current access control implementation
- [x] Plan-based restrictions already implemented in layout.html:
  - Herramientas: Available for all plans (básico, personal, profesional)
  - Reportes: Available for personal and profesional plans only
  - Planificador de Producción: Available for profesional plan only

### 5. Testing
- [ ] Test Básico plan flow (tools only)
- [ ] Test Personal plan flow (tools + reports)
- [ ] Test Profesional plan flow (tools + reports + production)
- [ ] Test Institucional plan flow (custom pricing)
- [ ] Verify payment integration works
- [ ] Test email notifications for all plan types

## Credentials from Image
- Admin: admin123 / admin123
- Juan Carlos Malinez: personal@example.com / admin123 (Personal plan)
- Douglas Ordoñez: douglas@gmail.com / admin123 (Básico plan)
- Administrador: admin@example.com / admin123 (Básico plan)
- Administrador FeedPro: admin@feedpro.com / admin123 (Personal plan)
- Personal: personal@feedpro.app / 123 (Personal plan)
- Básico: basico@feedpro.app / 123 (Básico plan)
- Profesional: profesional@feedpro.app / 123 (Profesional plan)

## Status
- [ ] Started
- [ ] In Progress  
- [ ] Testing
- [ ] Completed
