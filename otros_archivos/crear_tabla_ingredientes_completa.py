import mysql.connector
import pandas as pd

# Configuración de conexión
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "db_nutriapp",
    "user": "root",
    "password": "root1234"
}

def crear_tabla_ingredientes_completa():
    """Crear una nueva tabla con todas las columnas nutricionales del Excel"""
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Crear la nueva tabla con todas las columnas
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ingredientes_completos (
        ID INT PRIMARY KEY,
        INGREDIENTES VARCHAR(255),
        PRECIO TEXT,
        COMENTARIOS TEXT,
        MATERIA_SECA DECIMAL(8,4),
        HUMEDAD DECIMAL(8,4),
        CENIZAS DECIMAL(8,4),
        PB DECIMAL(8,4),
        EE DECIMAL(8,4),
        EE_VERD DECIMAL(8,4),
        FB DECIMAL(8,4),
        FND DECIMAL(8,4),
        FAD DECIMAL(8,4),
        LAD DECIMAL(8,4),
        ALMIDON DECIMAL(8,4),
        AZUCARES DECIMAL(8,4),
        SUMA DECIMAL(8,4),
        C14_0 DECIMAL(8,4),
        C16_0 DECIMAL(8,4),
        C16_1 DECIMAL(8,4),
        C18_0 DECIMAL(8,4),
        C18_1 DECIMAL(8,4),
        C18_2 DECIMAL(8,4),
        C18_3 DECIMAL(8,4),
        C_20 DECIMAL(8,4),
        Ca DECIMAL(8,4),
        P DECIMAL(8,4),
        P_fitico DECIMAL(8,4),
        P_disp_AVES DECIMAL(8,4),
        P_dig_AVES DECIMAL(8,4),
        P_dig_PORC DECIMAL(8,4),
        Na DECIMAL(8,4),
        Cl DECIMAL(8,4),
        Mg DECIMAL(8,4),
        K DECIMAL(8,4),
        S DECIMAL(8,4),
        Cu_ppm DECIMAL(8,4),
        Fe_ppm DECIMAL(8,4),
        Mn_ppm DECIMAL(8,4),
        Zn_ppm DECIMAL(8,4),
        Vit_E_ppm DECIMAL(8,4),
        Biotina_ppm DECIMAL(8,4),
        Colina_ppm DECIMAL(8,4),
        EM_RTES_Kcal_kg DECIMAL(8,4),
        UFL_UF_kg DECIMAL(8,4),
        UFC_UF_kg DECIMAL(8,4),
        ENL_RTES_Kcal_kg DECIMAL(8,4),
        ENM_RTES_Kcal_kg DECIMAL(8,4),
        ENC_RTES_Kcal_kg DECIMAL(8,4),
        ALM_SOLUBLE DECIMAL(8,4),
        ALM_DEGRAD DECIMAL(8,4),
        ED_PORC_Kcal_kg DECIMAL(8,4),
        EM_PORC_Kcal_kg DECIMAL(8,4),
        EN_PORC_Kcal_kg DECIMAL(8,4),
        EN_CERDAS_Kcal_kg DECIMAL(8,4),
        EMA_POLLIT_Kcal_kg DECIMAL(8,4),
        EMA_AVES_Kcal_kg DECIMAL(8,4),
        ED_CONEJOS_Kcal_kg DECIMAL(8,4),
        ED_CABALLO_Kcal_kg DECIMAL(8,4),
        PBDIG_RUM DECIMAL(8,4),
        PBDIG_PORC DECIMAL(8,4),
        PBDIG_AVES DECIMAL(8,4),
        PBDIG_CON DECIMAL(8,4),
        PBDIG_CAB DECIMAL(8,4),
        PDIA DECIMAL(8,4),
        PDIE DECIMAL(8,4),
        PDIN DECIMAL(8,4),
        LYS_PDIE DECIMAL(8,4),
        MET_PDIE DECIMAL(8,4),
        LYS DECIMAL(8,4),
        MET DECIMAL(8,4),
        M_C DECIMAL(8,4),
        THR DECIMAL(8,4),
        TRP DECIMAL(8,4),
        ILE DECIMAL(8,4),
        VAL DECIMAL(8,4),
        ARG DECIMAL(8,4),
        GLYeq DECIMAL(8,4),
        LYS_DIA DECIMAL(8,4),
        MET_DIA DECIMAL(8,4),
        M_C_DIA DECIMAL(8,4),
        THR_DIA DECIMAL(8,4),
        TRP_DIA DECIMAL(8,4),
        ILE_DIA DECIMAL(8,4),
        VAL_DIA DECIMAL(8,4),
        ARG_DIA DECIMAL(8,4),
        GLYeq_DIA DECIMAL(8,4),
        LYS_DIS DECIMAL(8,4),
        MET_DIS DECIMAL(8,4),
        M_C_DIS DECIMAL(8,4),
        THR_DIS DECIMAL(8,4),
        TRP_DIS DECIMAL(8,4),
        ILE_DIS DECIMAL(8,4),
        VAL_DIS DECIMAL(8,4),
        ARG_DIS DECIMAL(8,4),
        GLYeq_DIS DECIMAL(8,4),
        LYS_DR DECIMAL(8,4),
        MET_DR DECIMAL(8,4),
        M_C_DR DECIMAL(8,4),
        THR_DR DECIMAL(8,4),
        TRP_DR DECIMAL(8,4),
        ILE_DR DECIMAL(8,4),
        VAL_DR DECIMAL(8,4),
        ARG_DR DECIMAL(8,4),
        GLYeq_DR DECIMAL(8,4),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'ingredientes_completos' creada exitosamente")
        
        # Confirmar cambios
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")
    
    finally:
        cursor.close()
        conn.close()

def importar_datos_completos():
    """Importar todos los datos del Excel a la nueva tabla"""
    
    # Leer el archivo Excel
    df = pd.read_excel('Tabla de ingrediente PASAR.xlsx')
    
    # Conectar a la base de datos
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Limpiar tabla
    cursor.execute("DELETE FROM ingredientes_completos")
    
    imported_count = 0
    
    for index, row in df.iterrows():
        try:
            # Preparar valores para inserción
            values = []
            
            # Mapear cada columna del Excel
            column_mapping = {
                'ID': 'ID',
                'INGREDIENTES': 'INGREDIENTES', 
                'PRECIO': 'PRECIO',
                'COMENTARIOS': 'COMENTARIOS',
                'MATERIA_SECA_(%)': 'MATERIA_SECA',
                'HUMEDAD_(%)': 'HUMEDAD',
                'CENIZAS_(%)': 'CENIZAS',
                'PB_(%)': 'PB',
                'EE_(%)': 'EE',
                'EE_VERD_(%)': 'EE_VERD',
                'FB_(%)': 'FB',
                'FND_(%)': 'FND',
                'FAD_(%)': 'FAD',
                'LAD_(%)': 'LAD',
                'ALMIDON_(%)': 'ALMIDON',
                'AZUCARES_(%)': 'AZUCARES',
                'SUMA_(%)': 'SUMA',
                'C14:0_(%)': 'C14_0',
                'C16:0_(%)': 'C16_0',
                'C16:1_(%)': 'C16_1',
                'C18:0_(%)': 'C18_0',
                'C18:1_(%)': 'C18_1',
                'C18:2_(%)': 'C18_2',
                'C18:3_(%)': 'C18_3',
                'C>20_(%)': 'C_20',
                'Ca_(%)': 'Ca',
                'P_(%)': 'P',
                'Pfítico_(%)': 'P_fitico',
                'Pdisp_AVES_(%)': 'P_disp_AVES',
                'Pdig_AVES_(%)': 'P_dig_AVES',
                'Pdig_PORC_(%)': 'P_dig_PORC',
                'Na_(%)': 'Na',
                'Cl_(%)': 'Cl',
                'Mg_(%)': 'Mg',
                'K_(%)': 'K',
                'S_(%)': 'S',
                'Cu_(ppm)': 'Cu_ppm',
                'Fe_(ppm)': 'Fe_ppm',
                'Mn_(ppm)': 'Mn_ppm',
                'Zn_(ppm)': 'Zn_ppm',
                'Vit_E_(ppm)': 'Vit_E_ppm',
                'Biotina_(ppm)': 'Biotina_ppm',
                'Colina_(ppm)': 'Colina_ppm',
                'EM_RTES_(Kcal/kg)': 'EM_RTES_Kcal_kg',
                'UFL_(UF/kg)': 'UFL_UF_kg',
                'UFC_(UF/kg)': 'UFC_UF_kg',
                'ENL_RTES_(Kcal/kg)': 'ENL_RTES_Kcal_kg',
                'ENM_RTES_(Kcal/kg)': 'ENM_RTES_Kcal_kg',
                'ENC_RTES_(Kcal/kg)': 'ENC_RTES_Kcal_kg',
                'ALM_SOLUBLE_(%)': 'ALM_SOLUBLE',
                'ALM_DEGRAD_(%)': 'ALM_DEGRAD',
                'ED_PORC_(Kcal/kg)': 'ED_PORC_Kcal_kg',
                'EM_PORC_(Kcal/kg)': 'EM_PORC_Kcal_kg',
                'EN_PORC_(Kcal/kg)': 'EN_PORC_Kcal_kg',
                'EN_CERDAS_(Kcal/kg)': 'EN_CERDAS_Kcal_kg',
                'EMA_POLLIT_(Kcal/kg)': 'EMA_POLLIT_Kcal_kg',
                'EMA_AVES _(Kcal/kg)': 'EMA_AVES_Kcal_kg',
                'ED_CONEJOS_(Kcal/kg)': 'ED_CONEJOS_Kcal_kg',
                'ED_CABALLO_(Kcal/kg)': 'ED_CABALLO_Kcal_kg',
                'PBDIG_RUM_(%)': 'PBDIG_RUM',
                'PBDIG_PORC_(%)': 'PBDIG_PORC',
                'PBDIG_AVES_(%)': 'PBDIG_AVES',
                'PBDIG_CON_(%)': 'PBDIG_CON',
                'PBDIG_CAB_(%)': 'PBDIG_CAB',
                'PDIA_(%)': 'PDIA',
                'PDIE_(%)': 'PDIE',
                'PDIN_(%)': 'PDIN',
                'LYS_(%PDIE)': 'LYS_PDIE',
                'MET_(%PDIE)': 'MET_PDIE',
                'LYS_(%)': 'LYS',
                'MET_(%)': 'MET',
                'M+C_(%)': 'M_C',
                'THR_(%)': 'THR',
                'TRP_(%)': 'TRP',
                'ILE_(%)': 'ILE',
                'VAL_(%)': 'VAL',
                'ARG_(%)': 'ARG',
                'GLYeq_(%)': 'GLYeq',
                'LYS_DIA_(%)': 'LYS_DIA',
                'MET_DIA_(%)': 'MET_DIA',
                'M+C_DIA_(%)': 'M_C_DIA',
                'THR_DIA_(%)': 'THR_DIA',
                'TRP_DIA_(%)': 'TRP_DIA',
                'ILE_DIA_(%)': 'ILE_DIA',
                'VAL_DIA_(%)': 'VAL_DIA',
                'ARG_DIA_(%)': 'ARG_DIA',
                'GLYeq_DIA_(%)': 'GLYeq_DIA',
                'LYS_DIS_(%)': 'LYS_DIS',
                'MET_DIS_(%)': 'MET_DIS',
                'M+C_DIS_(%)': 'M_C_DIS',
                'THR_DIS_(%)': 'THR_DIS',
                'TRP_DIS_(%)': 'TRP_DIS',
                'ILE_DIS_(%)': 'ILE_DIS',
                'VAL_DIS_(%)': 'VAL_DIS',
                'ARG_DIS_(%)': 'ARG_DIS',
                'GLYeq_DIS_(%)': 'GLYeq_DIS',
                'LYS_DR_(%)': 'LYS_DR',
                'MET_DR_(%)': 'MET_DR',
                'M+C_DR_(%)': 'M_C_DR',
                'THR_DR_(%)': 'THR_DR',
                'TRP_DR_(%)': 'TRP_DR',
                'ILE_DR_(%)': 'ILE_DR',
                'VAL_DR_(%)': 'VAL_DR',
                'ARG_DR_(%)': 'ARG_DR',
                'GLYeq_DR_(%)': 'GLYeq_DR'
            }
            
            # Preparar valores para inserción
            for excel_col, db_col in column_mapping.items():
                if excel_col in ['INGREDIENTES', 'PRECIO', 'COMENTARIOS']:
                    # Campos de texto
                    val = str(row[excel_col]) if pd.notna(row[excel_col]) else None
                    if val == 'nan':
                        val = None
                    values.append(val)
                else:
                    # Campos numéricos
                    try:
                        if pd.isna(row[excel_col]) or str(row[excel_col]).strip() == '' or str(row[excel_col]).lower() == 'nan':
                            values.append(None)
                        else:
                            val = float(str(row[excel_col]).strip())
                            values.append(round(val, 4))
                    except (ValueError, TypeError):
                        values.append(None)
            
            # Crear la consulta SQL
            placeholders = ', '.join(['%s'] * len(values))
            columns = ', '.join(column_mapping.values())
            
            sql = f"INSERT INTO ingredientes_completos ({columns}) VALUES ({placeholders})"
            
            cursor.execute(sql, values)
            
            print(f"Insertado: {row['INGREDIENTES']}")
            imported_count += 1
            
        except Exception as e:
            print(f"Error procesando fila {index}: {e}")
            continue
    
    # Confirmar cambios
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Proceso completado. {imported_count} ingredientes importados a la nueva tabla.")

if __name__ == "__main__":
    print("🔄 Creando tabla completa de ingredientes...")
    crear_tabla_ingredientes_completa()
    
    print("\n🔄 Importando datos del Excel...")
    importar_datos_completos()
    
    print("\n✅ Proceso completado exitosamente!")
