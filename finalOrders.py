import boto3

import rekogOrders as r
import s3Orders as s
import dynamoDBOrders as d

def agregarDetalles(nombre):
    nombre = nombre.lower().replace(' ','_')
    nombre = 'alumno_'+nombre+'.jpg'
    return nombre

def main(table, curso, imageFile, listaAlumnos=[]):
    
    ### Agregar Alumnos al Curso ###
    if len(listaAlumnos) != 0:
        for i in range(len(listaAlumnos)):
            r.agregarAlumno(table, curso, agregarDetalles(listaAlumnos[i]))
    
    ### Realizar Comparación ###
    faceIdsList = r.comprarConColleccion(curso, imageFile)

    if faceIdsList != {}:
        for key, value in faceIdsList.items():
            name = d.getName(table, key)
            print('Alumno ' + name.replace('_',' ') + ' del curso ' + curso + ' se encuentra en esta foto con una probabilidad de ' + str(value) )
    else:
        print('No hubo coincidencia alguna')


if __name__ == "__main__":
    table = 'testtic3v2'
    curso = 'tics3'
    imageFile = './'+curso+'/09.jpg' 
    main(table, curso, imageFile)
