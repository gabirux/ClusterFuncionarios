import pyodbc 
import pandas as pd 
import numpy as np  
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Conexão com o SQL Server

server = 'localhost' 
database = 'FuncionarismoSP-DW' 
username = 'srv_app' 
password = 'Jx94@$D3' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

# Realiza query para busca dos dados de idade e sexo
query = "SELECT IDRegistro, S.Sexo AS Sexo, DATEDIFF(YEAR,D.Data,GETDATE()) AnosContratacao FROM fat.Contratacao AS C INNER JOIN dim.Data AS D ON C.IDData = D.IDData INNER JOIN dim.Sexo AS S ON C.IDSexo = S.IDSexo;"
df = pd.read_sql(query, cnxn)


# Remove as colunas IDRegistro e Sexo do dataset
dfresult = np.array(df.drop(['IDRegistro', 'Sexo'],axis = 1))

# Realiza clusterização com o algoritmo K-means
kmeans = KMeans(n_clusters=5, random_state=0)
kmeans.fit(dfresult)

df['cluster'] = kmeans.labels_


# Insere retorno da clusterização no SQL Server

cols = "`,`".join([str(i) for i in df.columns.tolist()])

for index, row in df.iterrows():
    cursor.execute("INSERT INTO ml.ClusterResultados (IDRegistro,Sexo,AnosContratacao,NumCluster) values(?,?,?,?)", row.IDRegistro, row.Sexo, row.AnosContratacao, row.cluster)
cnxn.commit()
cursor.close()
