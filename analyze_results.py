import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("medline_results.csv")
dfcran = pd.read_csv("datosElastic.csv")

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



# sns.boxplot(x="variable", y="value", hue="Operador", data=pd.melt(df[['Operador', 'Precision', 'Recall', 'F1', 'NDCG']], ['Operador']), palette='Set2', width=0.6)
# plt.title("Box Plots of Precision, Recall, F1, and NDCG by Operador")
# plt.xlabel("Metrics")
# plt.ylabel("Values")
# plt.show()


sns.boxplot(x="variable", y="value", hue="Operador", data=pd.melt(dfcran[['Operador', 'Precision', 'Recall', 'F1', 'NDCG']], ['Operador']), palette='Set2', width=0.6)
plt.title("Box Plots of Precision, Recall, F1, and NDCG by Operador")
plt.xlabel("Metrics")
plt.ylabel("Values")
plt.show()