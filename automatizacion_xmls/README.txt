Guía rápida para utilizar el programa mainNubebot y posibles errores cuando se ejecute.

El ejecutable mainNubebot lee los datos del archivo excel_input.xls (importante, tiene que ser ese nombre y ese formato) y genera los archivos .xml de los contratos de tratamiento de cada residuo y los guarda en la carpeta input, esto se usará después para ejecutar otro .exe que no está en esta carpeta.

Si la entidad medioambiental NO está registada en nubelus, el programa creará todo: esto es desde la entidad, los centros, clientes, proveedores, usuarios, autorizaciones, contratos de representación y tratamientos.

Si está registrada en nubelus se asume que tiene clientes y proveedores, si no los tuviera comprobarlo antes de correr el programa y una vez hecho esto ejecutarlo.

Si la entidad está registrada pero el dato de entrada es de un nuevo centro el programa creará el centro, sus autorizaciones y todo lo necesario hasta acabar con los contratos de tratamiento.

Esto cubre casi la totalidad de los casos de uso. También se han incluido en el programa otros casos:

Si la entidad, centro y usuario está registrado creará los contratos de representación y tratamientos.

Si el contrato de representación ya está solo creará los de tratamiento.

Si no están todos los contratos de tratamientos creará los que falta.

Por último, si en algún punto el programa falla avisará con un mensaje para continuar o no el programa. Es recomendable cerrar el programa siempre y comprobar que tanto los datos de entrada como alguno de los campos en nubelus están completos: por ejemplo el cliente y el proveedor. Una vez hecho esto se podría ejecutar otra vez el programa.

Al crear todos los contratos el programa finalizará.