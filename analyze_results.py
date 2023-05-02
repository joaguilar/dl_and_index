import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# dfmedline = pd.read_csv("datosElastic_medline.csv")
# dfmedline2 = pd.read_csv("datosNormOps_medline.csv")
# dfmedline.append(dfmedline2, ignore_index=True)

dfmedline = pd.concat(map(pd.read_csv, ["datosElastic_medline.csv","datosNormOps_medline.csv"]), ignore_index=True)
dfcran = pd.concat(map(pd.read_csv, ["datosElastic_cran.csv","datosNormOps_cran.csv"]), ignore_index=True)
dftime = pd.concat(map(pd.read_csv, ["datosElastic_time.csv","datosNormOps_time.csv"]), ignore_index=True)

# dfcran = pd.read_csv("datosElastic_cran.csv")
# dfcran2 = pd.read_csv("datosNormOps_cran.csv")
# dfcran.append(dfcran2, ignore_index=True)

# sns.boxplot(x="Operador", y="Precision", data=df)
# plt.title("Precision by Operador")
# plt.show()

# sns.boxplot(x="Operador", y="F1", data=df)
# plt.title("F1 by Operador")
# plt.show()


# sns.boxplot(x="Operador", y="NDCG", data=df)
# plt.title("NDCG by Operador")
# plt.show()

# sns.boxplot(x="Operador", y="NDCG", data=df)
# plt.title("NDCG by Operador")
# plt.show()



sns.boxplot(x="variable", y="value", hue="Operador", data=pd.melt(dfmedline[['Operador', 'Precision', 'Recall', 'F1', 'NDCG']], ['Operador']), palette='Set2', width=0.6)
plt.title("Medline: Box Plots of Precision, Recall, F1, and NDCG by Operador")
plt.xlabel("Metrics")
plt.ylabel("Values")
plt.show()


sns.boxplot(x="variable", y="value", hue="Operador", data=pd.melt(dfcran[['Operador', 'Precision', 'Recall', 'F1', 'NDCG']], ['Operador']), palette='Set2', width=0.6)
plt.title("Cran: Box Plots of Precision, Recall, F1, and NDCG by Operador")
plt.xlabel("Metrics")
plt.ylabel("Values")
plt.show()

sns.boxplot(x="variable", y="value", hue="Operador", data=pd.melt(dftime[['Operador', 'Precision', 'Recall', 'F1', 'NDCG']], ['Operador']), palette='Set2', width=0.6)
plt.title("Time: Box Plots of Precision, Recall, F1, and NDCG by Operador")
plt.xlabel("Metrics")
plt.ylabel("Values")
plt.show()

grouped = dfmedline.groupby('Operador')[['Precision', 'Recall', 'F1', 'NDCG']].mean()
grouped.plot(kind='bar')
plt.title('Medline: Comparison of Averages by Operator')
plt.xlabel('Operator')
plt.ylabel('Average Score')
plt.show()

grouped = dfcran.groupby('Operador')[['Precision', 'Recall', 'F1', 'NDCG']].mean()
grouped.plot(kind='bar')
plt.title('Cran: Comparison of Averages by Operator')
plt.xlabel('Operator')
plt.ylabel('Average Score')
plt.show()

grouped = dftime.groupby('Operador')[['Precision', 'Recall', 'F1', 'NDCG']].mean()
grouped.plot(kind='bar')
plt.title('Time: Comparison of Averages by Operator')
plt.xlabel('Operator')
plt.ylabel('Average Score')
plt.show()


grouped = dfmedline.groupby('Operador')[['Precision', 'Recall', 'F1', 'NDCG']].median()
grouped.plot(kind='bar')
plt.title('Medline: Comparison of Median by Operator')
plt.xlabel('Operator')
plt.ylabel('Median Score')
plt.show()

grouped = dfcran.groupby('Operador')[['Precision', 'Recall', 'F1', 'NDCG']].median()
grouped.plot(kind='bar')
plt.title('Cran: Comparison of Median by Operator')
plt.xlabel('Operator')
plt.ylabel('Median Score')
plt.show()

grouped = dftime.groupby('Operador')[['Precision', 'Recall', 'F1', 'NDCG']].median()
grouped.plot(kind='bar')
plt.title('Time: Comparison of Median by Operator')
plt.xlabel('Operator')
plt.ylabel('Median Score')
plt.show()