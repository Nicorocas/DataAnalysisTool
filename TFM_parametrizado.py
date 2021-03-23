import os
from arcpy import env
import arcpy
arcpy.env.overwriteOutput = True
env.overwriteOutput = True
#Se define el wrokspace de la carpeta donde se va a iterar
miworkspace= arcpy.GetParameterAsText(0) #variable carpeta donde estan los archivos
env.workspace= miworkspace
arcpy.env.overwriteOutput = True
#Se crea una GDB a la que iran los archivos que se van a sacar#
gdb_origen =  arcpy.GetParameterAsText(1) #variable donde se va a almacenar la GDB
nombre_GDB=  arcpy.GetParameterAsText(2) #Nombre de la GDB que se va a crear
NuevaGDB = arcpy.CreateFileGDB_management(gdb_origen, nombre_GDB)
NombreGDB = os.path.join(gdb_origen,nombre_GDB)
#la idea va ser añadir los archivos que se llamen rt_tramo_vial.shp y rt_nodoctra_p.shp a esa GDB#
### REFERENCIA ESPACIAL MALDITO DESASTREE###
#Codigo etrs89= 25830  WGS = 4326
etrs89 = arcpy.SpatialReference(25830)
wgs = arcpy.SpatialReference(3857)

#para hacerlo necesito el resultado de iterar en las carpetas dentro de la carpeta en dos bucles y en los nombres de cada archivo,
#un ListWorkspace para cada nivel
ListaCarpetas= arcpy.ListWorkspaces(workspace_type="Folder")

#y un ListfeatureClasses para cada workspace
ListasFeatureClass = arcpy.ListFeatureClasses(feature_type="Polyline")

#con estos dos elementos tenemos todos los nombres, hay que sacar la logica de iterar hasta el nivel de shapefile
for carpeta in ListaCarpetas: #cadaProvincia
    miNuevoWorkspace = carpeta
    env.workspace = miNuevoWorkspace  # se cambia el workspace
    arcpy.AddMessage(carpeta)
    arcpy.AddMessage("iterando en carpeta")

    ListaCarpetas = arcpy.ListWorkspaces(workspace_type="Folder")
    for carpetas in ListaCarpetas: #cada Tipo de Archivos
        miNuevoWorkspace = carpetas
        env.workspace = miNuevoWorkspace
        ListasFeatureClass = arcpy.ListFeatureClasses()

        #ListfeatureClasses para rt_tramo_vial.shp y ahora para los nodos rt_nodoctra_p.shp
        #ListfeatureClasses en cada carpeta y si es el correcto se añade a la GDB
        for FeatureClass in ListasFeatureClass:
            if FeatureClass == "rt_tramo_vial.shp":
                arcpy.FeatureClassToGeodatabase_conversion(FeatureClass,NuevaGDB)
                arcpy.AddMessage("cargando rt_tramo_vial a GDB")
            if FeatureClass == "rt_nodoctra_p.shp":
                arcpy.FeatureClassToGeodatabase_conversion(FeatureClass, NuevaGDB)
                arcpy.AddMessage("cargando rt_nodoctra_p.shp a GDB")
#ya estan las FC en la GDB, ahora vamos a unirlas en un merge para luego tener que manejar sola una FC en la GDB
arcpy.env.overwriteOutput = True
arcpy.env.overwriteOutput = True
env.workspace = NombreGDB

#primero listamos las lineas rt_tramo_vial
listaGDB_lineas = arcpy.ListFeatureClasses(feature_type="Polyline")
arcpy.AddMessage(listaGDB_lineas)
#añadimos los archivos listados en la nueva GDB
FC = arcpy.CreateFeatureclass_management(NuevaGDB,"Rt_definitivo","POLYLINE")
arcpy.Merge_management(listaGDB_lineas, FC)

#Ahora lo mismo pero para la clase de entidad de nodo
listaGDB_puntos = arcpy.ListFeatureClasses(feature_type="Point")
arcpy.AddMessage(listaGDB_puntos)
#listamos los archivos incorporados en la nueva GDB
FC = arcpy.CreateFeatureclass_management(NuevaGDB,"Rt_nodo_definitivo","POINT")
arcpy.Merge_management(listaGDB_puntos, FC)
NuevaFC = "Rt_definitivo.shp"
NuevaFCNodo = "Rt_nodo_definitivo.shp"
arcpy.AddMessage("Merge completado tutobenne")

#reproyectar las capas a WGS84 para hacerla compatible con el resto del proyecto en ArcgisOnline, y borrar datos sobrantes
env.workspace = NombreGDB
NuevaFCa = arcpy.ListFeatureClasses()
for fc in NuevaFCa:
    if fc == "Rt_definitivo":
        arcpy.Project_management(fc, "Rt_definitivo1", wgs)
        arcpy.AddMessage("capa reproyectada")
        arcpy.Delete_management(fc)
        arcpy.AddMessage(fc+" Borrada")
    if fc == "Rt_nodo_definitivo":
        arcpy.Project_management(fc, "Rt_nodo_definitivo1", wgs)
        arcpy.AddMessage("capa reproyectada")
        arcpy.Delete_management(fc)
        arcpy.AddMessage(fc + " Borrada")
    else:
        #borrar datos sobrantes
        arcpy.Delete_management(fc)
        arcpy.AddMessage(fc+" borrada")

NuevaFC = "Rt_definitivo1"
#Para Addfield tenemos que establecer unas variables y rellenar los campos en la capa de lineas
Nombre_campo= "velocidad_coches"
Nombre_campo1= "velocidad_ciclomotor"
Nombre_campo2= "prohibido_bicis"
Nombre_campo3= "prohibido_coches"
Nombre_campo4= "tiempo_coches"
Nombre_campo5= "tiempo_ciclomotor"
Nombre_campo6= "consumo_coche"
Nombre_campo7= "consumo_moto"

#Field type
Field_type_text ="TEXT"
Field_type_Numero = "DOUBLE"

#hay que añadir 7 campos asique seran 7 addfields cada uno con su config, e ir añadiendo el CalculatedField
#Campo 0 Velocidad coches
arcpy.AddField_management(NuevaFC,Nombre_campo,Field_type_Numero)
tabla= NuevaFC
campo = Nombre_campo
expresion= "velocidad(!claseD!)"
tipo_expresion = "PYTHON3"
Codigo_bloque ="""def velocidad(incognita):

    if incognita == "Autopista":
        return 120
    if incognita == "Autovía":
        return 120
    if incognita == "Camino":
        return 20
    if incognita == "Carretera convencional":
        return 90
    if incognita == "Carretera multicarril":
        return 90
    if incognita == "Carril bici":
        return  5
    if incognita == "Senda":
        return 5
    if incognita == "Urbano":
        return 50
"""
tipo_campo = Field_type_Numero
arcpy.CalculateField_management(tabla,campo,expresion,tipo_expresion,Codigo_bloque,tipo_campo)
arcpy.AddMessage("campo velocidad coche añadido")
#Campo 1 Velocidad ciclomotor
arcpy.AddField_management(NuevaFC,Nombre_campo1,Field_type_Numero)
tabla= NuevaFC
campo = Nombre_campo1
expresion= "velocidad(!claseD!)"
tipo_expresion = "PYTHON3"
Codigo_bloque ="""def velocidad(incognita):

    if incognita == "Autopista":
        return 5
    if incognita == "Autovía":
        return 5
    if incognita == "Camino":
        return 20
    if incognita == "Carretera convencional":
        return 60
    if incognita == "Carretera multicarril":
        return 60
    if incognita == "Carril bici":
        return  40
    if incognita == "Senda":
        return 30
    if incognita == "Urbano":
        return 50
"""
tipo_campo = Field_type_Numero
arcpy.CalculateField_management(tabla,campo,expresion,tipo_expresion,Codigo_bloque,tipo_campo)
arcpy.AddMessage("campo velocidad moto añadido")
#campo4 tiempo en coche
arcpy.AddField_management(NuevaFC,Nombre_campo4,Field_type_Numero)
tabla= NuevaFC
campo = Nombre_campo4
expresion= "tiempo_coche(!Shape_Length!,!velocidad_coches!)"
tipo_expresion = "PYTHON3"
Codigo_bloque ="""def tiempo_coche(espacio,velocidad):
    return (espacio/(velocidad*1000))
"""
tipo_campo = Field_type_Numero
arcpy.CalculateField_management(tabla,campo,expresion,tipo_expresion,Codigo_bloque,tipo_campo)
arcpy.AddMessage("campo tiempo en coche añadido")
#campo5 tiempo ciclomotor
arcpy.AddField_management(NuevaFC,Nombre_campo5,Field_type_Numero)
tabla= NuevaFC
campo = Nombre_campo5
expresion= "tiempo_ciclomotor(!Shape_Length!,!velocidad_ciclomotor!)"
tipo_expresion = "PYTHON3"
Codigo_bloque ="""def tiempo_ciclomotor(espacio,velocidad):
    return (espacio/(velocidad*1000))
"""
tipo_campo = Field_type_Numero
arcpy.CalculateField_management(tabla,campo,expresion,tipo_expresion,Codigo_bloque,tipo_campo)
arcpy.AddMessage("campo tiempo en moto añadido")
#Campo6 consumo coche
arcpy.AddField_management(NuevaFC,Nombre_campo6,Field_type_Numero)
tabla= NuevaFC
campo = Nombre_campo6
expresion= "consumo_coches(!Shape_Length!)"
tipo_expresion = "PYTHON3"
Codigo_bloque ="""def consumo_coches(campo1): #14kwh/100000m
    return (14*campo1)/100000
"""
tipo_campo = Field_type_Numero
arcpy.CalculateField_management(tabla,campo,expresion,tipo_expresion,Codigo_bloque,tipo_campo)
arcpy.AddMessage("campo consumo coches añadido")
#Campo7 consumo moto
arcpy.AddField_management(NuevaFC,Nombre_campo7,Field_type_Numero)
tabla= NuevaFC
campo = Nombre_campo7
expresion= "consumo_motos(!Shape_Length!)"
tipo_expresion = "PYTHON3"
Codigo_bloque ="""
def consumo_motos(campo1): #2KWh/100000m
    return (2*campo1)/100000
"""
tipo_campo = Field_type_Numero
arcpy.CalculateField_management(tabla,campo,expresion,tipo_expresion,Codigo_bloque,tipo_campo)
arcpy.AddMessage("campo consumo motos añadido")
#Campo2 prohibido coches
arcpy.AddField_management(NuevaFC,Nombre_campo2,Field_type_text)
tabla= NuevaFC
campo = Nombre_campo2
expresion= "Prohibido_coches(!claseD!,!tipovehicD!)"
tipo_expresion = "PYTHON3"
Codigo_bloque ="""def Prohibido_coches(incognita,campo2):

    if incognita == "Carril bici":
        return "Si"
    if incognita == "Senda":
        return "Si"
    if campo2 == "Peatón+bici":
        return "Si"
    else:
        return "No"
"""
tipo_campo = Field_type_text
arcpy.CalculateField_management(tabla,campo,expresion,tipo_expresion,Codigo_bloque,tipo_campo)
arcpy.AddMessage("campo prohibido coches añadido")
#Campo3 prohibido bicis
arcpy.AddField_management(NuevaFC,Nombre_campo3,Field_type_text)
tabla= NuevaFC
campo = Nombre_campo3
expresion= "Prohibido_bicis(!claseD!,!tipovehicD!)"
tipo_expresion = "PYTHON3"
Codigo_bloque ="""def Prohibido_bicis(campo1, campo2):
    if campo1 == "Autopista" or "Autovía" or "Carretera multicarril" :
        return "Si"
    if campo2 == "Solo vehículo":
        return "Si"
    else:
        return "No"
"""
tipo_campo = Field_type_text
arcpy.CalculateField_management(tabla,campo,expresion,tipo_expresion,Codigo_bloque,tipo_campo)
arcpy.AddMessage("campo prohibido bicis añadido")

#Ya estas los campos nuevos añadidos y calculados al nuevo shape de Rt_definitivo1,
# con esta Feature class y con la de rtnodos es con la que haremos el network dataset y posteriormente construiremos la red
# para ello necesitamis 1. Un Feature dataset, 2. Un netowrk Dataset construido con Rt_definitivo1 y rt_nodos_definitivo1
# 1. Feature Dataset#

NuevaFC = "Rt_definitivo1"
NuevaFCNodo = "Rt_nodo_definitivo1"
Salida_dataset = NombreGDB
Nombre = "FeatureDataset"
#Referencia_espacial = "opcional"
arcpy.CreateFeatureDataset_management(Salida_dataset,Nombre,wgs)
arcpy.AddMessage("se ha creado el Feature dataset")
#Feature class to Feature Dataset, para introducir Rt-definitivo a un feature dataset
GDB = Salida_dataset
arcpy.env.workspace = GDB

#introducimos las capas de lineas y nodos
FeatureDataset = os.path.join(GDB,Nombre)
Clase_entrada = os.path.join(GDB,NuevaFC)
Clase_entrada1 = os.path.join(GDB,NuevaFCNodo)
FeatureDataset_destino = FeatureDataset
arcpy.FeatureClassToGeodatabase_conversion([Clase_entrada,Clase_entrada1],FeatureDataset_destino)
arcpy.AddMessage("El pájaro esta en nido")
#comprobar si la FC esta en el feature Dataset
# 2. Crear el network dataset
Name = "NetworkDataset"
arcpy.env.workspace= FeatureDataset
nueva_clase_lineas= "Rt_definitivo1_1"
nueva_clase_nodos= "Rt_nodo_definitivo1_1"
arcpy.CreateNetworkDataset_na(FeatureDataset,Name,[nueva_clase_nodos,nueva_clase_lineas])
arcpy.AddMessage("Se ha creado el NetworkDataset")
