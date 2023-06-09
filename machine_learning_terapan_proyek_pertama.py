# -*- coding: utf-8 -*-
"""Machine Learning Terapan: Proyek Pertama.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nJOQEU8pIiGu9LQ6kslVjXfDkGBPAXTC

# Home Credit Default Risk

By Daffa Muhamad Azhar
"""

# Menyambungkan ke Google Drive
from google.colab import drive
drive.mount('/content/drive')

root = '/content/drive/MyDrive/Colab Notebooks/Dicoding/Dataset/Home Credit/'

"""## Import Data"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# tabel setting
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

app_train = pd.read_csv(root + 'application_train.csv')
bureau = pd.read_csv(root + 'bureau.csv')
pos_cash_balance = pd.read_csv(root + 'POS_CASH_balance.csv')
previous_application = pd.read_csv(root + 'previous_application.csv')

"""## Exploratory Data Analysis

### Application Train

Melihat data dari application_train
"""

app_train.head()

print('Jumlah baris : ', app_train.shape[0], 'data')
print('Jumlah kolom : ', app_train.shape[1], 'kolom')

app_train.describe()

app_train.dtypes

"""Melakukan pemeriksaan data"""

# Cek Missing Data
total_missing = app_train.isnull().sum().sort_values(ascending=False)
percent_1 = app_train.isnull().sum()/app_train.isnull().count()*100
percent_2 = (round(percent_1, 1)).sort_values(ascending=False)
missing_data = pd.concat([total_missing, percent_2], axis=1, keys=['Total Missing', '%'])
missing_data = missing_data.reset_index().rename(columns={'index': 'Column'})
missing_data

"""Terdapat banyak kolom yang memiliki persentase missing value yang sangat tinggi. Kolom tersebut dapat di-drop ataupun dilakukan imputing saat dilakukan pre-proses data.

Kemudian melakukan pengecekan TARGET
"""

app_target = pd.DataFrame(app_train.groupby('TARGET').size(), columns=['Count'])
app_target = app_target.sort_values(by=['Count'], ascending=False)
app_target = app_target.reset_index().rename(columns={'index': 'TARGET'})
app_target

"""Terdapat 282.686 data dengan TARGET 0 atau Pemohon dapat membayar pinjamannya dan 24.825 data dengan TARGET 1 atau Pemohon akan gagal bayar atau berkendala saat pembayaran."""

fig = px.pie(app_train, names='TARGET',)
fig.update_layout(title='Persentase dari TARGET')
fig.show()

"""Dilihat dari Pie Chart diatas, TARGET sangat tidak seimbang. Beberapa pendekatan yang dapat dilakukan yaitu oversampling (menaikkan data dengan TARGET 0) dan undersampling (memangkas data dengan TARGET 1)."""

kolom_1 = [
    'CODE_GENDER',
    'NAME_CONTRACT_TYPE',
    'FLAG_OWN_CAR',
    'FLAG_OWN_REALTY',
]

y = 2
x = 2
fig, ax = plt.subplots(y, x, figsize = (10,10))

i = 0
j = 0
for col in kolom_1:
  plot = sns.histplot(data=app_train, x=col, hue="TARGET", ax=ax[j][i])
  if i == x-1:
    i = 0
    j += 1
  else:
    i += 1

"""Terdapat anomali pada Gender yaitu terdapat Value XNA."""

kolom_2 = [
    'CNT_CHILDREN',
    'CNT_FAM_MEMBERS',
    'OCCUPATION_TYPE',
    'NAME_INCOME_TYPE',
    'NAME_TYPE_SUITE',
    'NAME_FAMILY_STATUS',
    'NAME_HOUSING_TYPE',
    'NAME_EDUCATION_TYPE',
]

y = 4
x = 2
fig, ax = plt.subplots(y, x, figsize = (30,20))

i = 0
j = 0
for col in kolom_2:
  plot = sns.countplot(data=app_train, y=col, hue="TARGET", ax=ax[j][i])
  ax[j][i].title.set_text(col)
  if i == x-1:
    i = 0
    j += 1
  else:
    i += 1

fig, ax = plt.subplots(1, 1, figsize = (10,10))

sns.boxplot(data=app_train, x='TARGET', y='AMT_CREDIT', ax=ax)
plt.show()

"""Melihat AMT_CREDIT dari beberapa sisi"""

fig, ax = plt.subplots(1, 1, figsize = (10,10))

sns.boxplot(data=app_train, x='AMT_CREDIT', y='OCCUPATION_TYPE', hue='TARGET', ax=ax)
plt.show()

fig, ax = plt.subplots(1, 1, figsize = (10,10))

sns.boxplot(data=app_train, x='AMT_CREDIT', y='NAME_INCOME_TYPE', hue='TARGET', ax=ax)
plt.show()

plt.hist(app_train['DAYS_BIRTH'] / 365, edgecolor = 'k', bins = 25)
plt.title('Age of Client'); plt.xlabel('Age (years)'); plt.ylabel('Count');

"""Usia pada data bernilai negatif maka harus dilakukan perbaikan. Dan pemohon paling banyak adalah pada usia 40 tahun. """

app_train['DAYS_BIRTH'] = abs(app_train['DAYS_BIRTH'])
plt.hist(app_train['DAYS_BIRTH'] / 365, edgecolor = 'k', bins = 25)
plt.title('Age of Client'); plt.xlabel('Age (years)'); plt.ylabel('Count');

plt.figure(figsize=(8,3))
sns.kdeplot(app_train.loc[app_train['TARGET'] == 0, 'DAYS_BIRTH'] / 365, label="Target 0", color='green')
sns.kdeplot(app_train.loc[app_train['TARGET'] == 1, 'DAYS_BIRTH'] / 365, label="Target 1", color='red')
plt.legend()
plt.show()

"""Setelah dilakukan perbaikan, dapat dilihat bahwa pemohon terbanyak berada diusia 30 hingga 40 tahun.

Dapat dilihat pada `app_train.describe()`, terdapat pemohon yang memiliki waktu bekerja selama 365.243 hari (1000 tahun) dan tidak bernilai negatif seperti data yang lainnya.
"""

app_train[app_train['DAYS_EMPLOYED'] == 365243].DAYS_EMPLOYED.count()

"""Terdapat 55.374 data pemohon dengan total hari kerja 1000 tahun. 

Untuk kasus ini akan dilakukan imputing untuk data hari kerja yang anomali dengan rata - rata hari kerja jika data yang anomali tidak ada.
"""

anom = app_train[app_train['DAYS_EMPLOYED'] == 365243]
non_anom = app_train[app_train['DAYS_EMPLOYED'] != 365243]

app_train['DAYS_EMPLOYED'] = app_train['DAYS_EMPLOYED'].apply(lambda x: non_anom['DAYS_EMPLOYED'].mean() if x == 365243 else x)

app_train['DAYS_EMPLOYED'] = abs(app_train['DAYS_EMPLOYED'])
plt.hist(app_train['DAYS_EMPLOYED'] / 365, edgecolor = 'k', bins = 25)
plt.title('Tahun Kerja'); plt.xlabel('Tahun (years)'); plt.ylabel('Count');

"""Persebaran data tidak akan tepat karena 55.374 data diimput dengan rata - rata.

Nilai density dari external source
"""

target_0_ext_source_1 = app_train[app_train['TARGET'] == 0]['EXT_SOURCE_1'].values
target_1_ext_source_1 = app_train[app_train['TARGET'] == 1]['EXT_SOURCE_1'].values

plt.figure(figsize=(8,3))
sns.kdeplot(target_0_ext_source_1, label="Target 0", color='green')
sns.kdeplot(target_1_ext_source_1, label="Target 1", color='red')
plt.legend()
plt.show()

target_0_ext_source_1 = app_train[app_train['TARGET'] == 0]['EXT_SOURCE_2'].values
target_1_ext_source_1 = app_train[app_train['TARGET'] == 1]['EXT_SOURCE_2'].values

plt.figure(figsize=(8,3))
sns.kdeplot(target_0_ext_source_1, label="Target 0", color='green')
sns.kdeplot(target_1_ext_source_1, label="Target 1", color='red')
plt.legend()
plt.show()

target_0_ext_source_1 = app_train[app_train['TARGET'] == 0]['EXT_SOURCE_3'].values
target_1_ext_source_1 = app_train[app_train['TARGET'] == 1]['EXT_SOURCE_3'].values

plt.figure(figsize=(8,3))
sns.kdeplot(target_0_ext_source_1, label="Target 0", color='green')
sns.kdeplot(target_1_ext_source_1, label="Target 1", color='red')
plt.legend()
plt.show()

"""### Bureau"""

bureau.head()

bureau.info()

print('Jumlah baris : ', bureau.shape[0], 'data')
print('Jumlah kolom : ', bureau.shape[1], 'kolom')

num = bureau.select_dtypes(include="number").columns.tolist() # memisahkan kolom numerik
cat = bureau.select_dtypes(include="object").columns.tolist() # memishakan kolom kategorik

bureau_categoric = bureau.loc[:, cat]

y = 2
x = 2
fig, ax = plt.subplots(y, x, figsize = (30,10))

i = 0
j = 0
for col in bureau_categoric:
  plot = sns.countplot(data=bureau, y=col, ax=ax[j][i])
  ax[j][i].title.set_text(col)
  if i == x-1:
    i = 0
    j += 1
  else:
    i += 1

bureau[num].describe().T

bureau[cat].describe().T

"""### Previous Application"""

previous_application.head()

previous_application.info()

print('Jumlah baris : ', previous_application.shape[0], 'data')
print('Jumlah kolom : ', previous_application.shape[1], 'kolom')

num = previous_application.select_dtypes(include="number").columns.tolist() # memisahkan kolom numerik
cat = previous_application.select_dtypes(include="object").columns.tolist() # memishakan kolom kategori

cat.remove('FLAG_LAST_APPL_PER_CONTRACT')
cat

y = 8
x = 2
fig, ax = plt.subplots(y, x, figsize = (30,50))

i = 0
j = 0
for col in cat:
  plot = sns.countplot(data=previous_application, y=col, ax=ax[j][i])
  ax[j][i].title.set_text(col)
  if i == x-1:
    i = 0
    j += 1
  else:
    i += 1

previous_application[num].describe().T

previous_application[cat].describe().T

"""### POS Cash Balance"""

pos_cash_balance.head()

pos_cash_balance.info()

print('Jumlah baris : ', pos_cash_balance.shape[0], 'data')
print('Jumlah kolom : ', pos_cash_balance.shape[1], 'kolom')

num = pos_cash_balance.select_dtypes(include="number").columns.tolist() # memisahkan kolom numerik
cat = pos_cash_balance.select_dtypes(include="object").columns.tolist() # memishakan kolom kategori

y = 1
x = 1
fig, ax = plt.subplots(y, x, figsize = (30,10))

i = 0
j = 0
for col in cat:
  plot = sns.countplot(data=pos_cash_balance, y=col, ax=ax)
  ax.title.set_text(col)

pos_cash_balance[num].describe().T

pos_cash_balance[cat].describe().T

"""## Data Preparation

### Handle Missing Value

Mengisi value dengan 0 pada kolom `EXT_SOURCE_1` karena fitur tersebut berisikan nilai dari hasil normalisasi tabel lain sehingga sangat dibutuhkan.
"""

# fillna ext source 1 dengan 0
app_train['EXT_SOURCE_1'] = app_train['EXT_SOURCE_1'].fillna(0)

"""Melakukan Drop kolom dengan missing value lebih dari 40% karena tidak akan banyak data yang hilang jika melakukan drop kolom ini."""

# Drop kolom dengan missing value >40%
app_train = app_train.drop(app_train.columns[app_train.isnull().mean() > 0.40], axis=1)

"""Drop data dimana `TARGET == 0` dan terdapat nilai `NULL`"""

# Cek Missing Data
total_missing = app_train.isnull().sum().sort_values(ascending=False)
percent_1 = app_train.isnull().sum()/app_train.isnull().count()*100
percent_2 = (round(percent_1, 1)).sort_values(ascending=False)
missing_data = pd.concat([total_missing, percent_2], axis=1, keys=['Total Missing', '%'])
missing_data = missing_data.reset_index().rename(columns={'index': 'Column'})
missing_data

# Delete row jika semua value-nya null
app_train = app_train.dropna(how='all')

# drop rows dengan target 0 yang memiliki Null value pada kolom yang memiliki null value.
index = app_train[
    (app_train['TARGET'] == 0) & 
    ( (app_train[missing_data['Column'][0]].isnull()) | 
     (app_train[missing_data['Column'][1]].isnull()) | 
     (app_train[missing_data['Column'][2]].isnull()) |
     (app_train[missing_data['Column'][3]].isnull()) |
     (app_train[missing_data['Column'][4]].isnull()) |
     (app_train[missing_data['Column'][5]].isnull()) |
     (app_train[missing_data['Column'][6]].isnull()) |
     (app_train[missing_data['Column'][7]].isnull())
     )].index
app_train = app_train.drop(index)

"""Hapus data dengan gender XNA"""

# XNA pada Gender Code
app_train[app_train['CODE_GENDER'] == 'XNA']

"""Berhubung kedua data tersebut memiliki TARGET 0 maka drop dilakukan ke seluruh data tersebut."""

# Drop rows dengan gender XNA
app_train = app_train.drop(app_train[app_train['CODE_GENDER'] == 'XNA'].index, axis=0)

"""Melakukan Imputing kepada sisa kolom yang terdapat missing value"""

# Generate data untuk Count Family Members
app_train['CNT_FAM_MEMBERS'] = app_train['CNT_FAM_MEMBERS'].fillna(app_train[app_train['CNT_CHILDREN'] == 0].CNT_FAM_MEMBERS.mode()[0])

# Generate Occupation Type missing value dengan Modus
app_train['OCCUPATION_TYPE'] = app_train['OCCUPATION_TYPE'].fillna(app_train['OCCUPATION_TYPE'].mode()[0])
app_train['NAME_TYPE_SUITE'] = app_train['NAME_TYPE_SUITE'].fillna(app_train['NAME_TYPE_SUITE'].mode()[0])

# fill semua kolom dengan 0
app_train = app_train.fillna(0)

# Cek Missing Data
total_missing = app_train.isnull().sum().sort_values(ascending=False)
percent_1 = app_train.isnull().sum()/app_train.isnull().count()*100
percent_2 = (round(percent_1, 1)).sort_values(ascending=False)
missing_data = pd.concat([total_missing, percent_2], axis=1, keys=['Total Missing', '%'])
missing_data = missing_data.reset_index().rename(columns={'index': 'Column'})
missing_data

app_train.shape

"""### Feature Engineering

Ketika data pada tabel utama sudah bersih, maka dilakukan feature engineering untuk menambah fitur baik dari tabel lain maupun dari tabel sendiri.

#### Menambahkan fitur yang diduga dapat meningkatkan kinerja model
"""

# New Feature Percentage
app_train['CREDIT_INCOME_PERCENT'] = app_train['AMT_CREDIT'] / app_train['AMT_INCOME_TOTAL']
app_train['ANNUITY_INCOME_PERCENT'] = app_train['AMT_ANNUITY'] / app_train['AMT_INCOME_TOTAL']
app_train['CREDIT_TERM'] = app_train['AMT_ANNUITY'] / app_train['AMT_CREDIT']
app_train['DAYS_EMPLOYED_PERCENT'] = app_train['DAYS_EMPLOYED'] / app_train['DAYS_BIRTH']

# replace infinite
app_train.replace([np.inf, -np.inf], 0, inplace=True)

# Drop Kolom FLAG DOCUMENTS yang persebaran data sangat imbalance
app_train = app_train.drop([
    'FLAG_DOCUMENT_2', 'FLAG_DOCUMENT_4', 'FLAG_DOCUMENT_5', 'FLAG_DOCUMENT_6', 'FLAG_DOCUMENT_7',
    'FLAG_DOCUMENT_8', 'FLAG_DOCUMENT_9', 'FLAG_DOCUMENT_10', 'FLAG_DOCUMENT_11', 'FLAG_DOCUMENT_12','FLAG_DOCUMENT_13',
    'FLAG_DOCUMENT_14', 'FLAG_DOCUMENT_15', 'FLAG_DOCUMENT_16', 'FLAG_DOCUMENT_17', 'FLAG_DOCUMENT_18','FLAG_DOCUMENT_19',
    'FLAG_DOCUMENT_20', 'FLAG_DOCUMENT_21'
], axis=1)

app_train.shape

"""#### Menambahkan fitur dari data Bureau

Total peminjaman yang terdapat pada biro kredit
"""

prev_loans = bureau.groupby('SK_ID_CURR', as_index=False)['SK_ID_BUREAU'].count().rename(columns = {'SK_ID_BUREAU': 'PREV_LOANS'})
prev_loans.head()

# jika tidak pernah meminjam sebelumnya
prev_loans['PREV_LOANS'] = prev_loans['PREV_LOANS'].fillna(0)

"""Total tipe kredit yang pernah dilakukan oleh pemohon"""

# Total Credit Types setiap nasabah
credit_types_per_customer = bureau[['SK_ID_CURR','CREDIT_TYPE']].groupby(by=['SK_ID_CURR'])['CREDIT_TYPE'].nunique()
credit_types_per_customer = credit_types_per_customer.reset_index().rename(columns={'CREDIT_TYPE':'PREV_TOTAL_CREDIT_TYPES'})
credit_types_per_customer.head()

# merge
prev_loans = prev_loans.merge(credit_types_per_customer, on = 'SK_ID_CURR', how = 'left')
prev_loans.head()

"""Menambahkan rata - rata jumlah tipe peminjaman"""

prev_loans['PREV_AVG_LOAN_TYPE'] = prev_loans['PREV_LOANS']/prev_loans['PREV_TOTAL_CREDIT_TYPES']
prev_loans.head()

"""Menambahkan modus dari tipe peminjaman sebelumnya"""

import scipy

# Modus dari prev Credit Types
mode_type = bureau[['SK_ID_CURR','CREDIT_TYPE']].groupby(by=['SK_ID_CURR'])['CREDIT_TYPE'].agg(lambda x:scipy.stats.mode(x)[0]).str[0]
mode_type = mode_type.reset_index().rename(columns={'CREDIT_TYPE':'PREV_CREDIT_TYPE_MODE'})
# mode_type['PREV_CREDIT_TYPE_MODE'] = mode_type['PREV_CREDIT_TYPE_MODE'].apply(lambda x: x[0] if type(x) == 'list' else x)
mode_type.head()

# Merge
prev_loans = prev_loans.merge(mode_type, on = 'SK_ID_CURR', how = 'left')
prev_loans.head()

"""Menambahkan jumlah setiap `ACTIVE_CREDIT` menjadi fitur"""

# Total Prev Closed Credit
index = bureau[
    (bureau['CREDIT_ACTIVE'] == 'Active') |
    (bureau['CREDIT_ACTIVE'] == 'Sold') |
    (bureau['CREDIT_ACTIVE'] == 'Bad debt')
].index

closed_credit = bureau.drop(index)

closed_credit = closed_credit[['SK_ID_CURR','CREDIT_ACTIVE']].groupby(by=['SK_ID_CURR'])['CREDIT_ACTIVE'].count()
closed_credit = closed_credit.reset_index().rename(columns={'CREDIT_ACTIVE':'PREV_CREDIT_CLOSED'})
closed_credit.head()

# Total Prev Active Credit
index = bureau[
    (bureau['CREDIT_ACTIVE'] == 'Closed') |
    (bureau['CREDIT_ACTIVE'] == 'Sold') |
    (bureau['CREDIT_ACTIVE'] == 'Bad debt')
].index

active_credit = bureau.drop(index)

active_credit = active_credit[['SK_ID_CURR','CREDIT_ACTIVE']].groupby(by=['SK_ID_CURR'])['CREDIT_ACTIVE'].count()
active_credit = active_credit.reset_index().rename(columns={'CREDIT_ACTIVE':'PREV_CREDIT_ACTIVE'})
active_credit.head()

# Total Prev Sold Credit
index = bureau[
    (bureau['CREDIT_ACTIVE'] == 'Active') |
    (bureau['CREDIT_ACTIVE'] == 'Closed') |
    (bureau['CREDIT_ACTIVE'] == 'Bad debt')
].index

sold_credit = bureau.drop(index)

sold_credit = sold_credit[['SK_ID_CURR','CREDIT_ACTIVE']].groupby(by=['SK_ID_CURR'])['CREDIT_ACTIVE'].count()
sold_credit = sold_credit.reset_index().rename(columns={'CREDIT_ACTIVE':'PREV_CREDIT_SOLD'})
sold_credit.head()

# Total Prev Bad Debt Credit
index = bureau[
    (bureau['CREDIT_ACTIVE'] == 'Active') |
    (bureau['CREDIT_ACTIVE'] == 'Closed') |
    (bureau['CREDIT_ACTIVE'] == 'Sold')
].index

bd_credit = bureau.drop(index)

bd_credit = bd_credit[['SK_ID_CURR','CREDIT_ACTIVE']].groupby(by=['SK_ID_CURR'])['CREDIT_ACTIVE'].count()
bd_credit = bd_credit.reset_index().rename(columns={'CREDIT_ACTIVE':'PREV_CREDIT_BAD_DEBT'})
bd_credit.head()

# Merge
prev_loans = prev_loans.merge(active_credit, on = 'SK_ID_CURR', how = 'left')
prev_loans = prev_loans.merge(closed_credit, on = 'SK_ID_CURR', how = 'left')
prev_loans = prev_loans.merge(sold_credit, on = 'SK_ID_CURR', how = 'left')
prev_loans = prev_loans.merge(bd_credit, on = 'SK_ID_CURR', how = 'left')
prev_loans.head()

# isi data yang kosong
prev_loans['PREV_CREDIT_ACTIVE'] = prev_loans['PREV_CREDIT_ACTIVE'].fillna(0)
prev_loans['PREV_CREDIT_CLOSED'] = prev_loans['PREV_CREDIT_CLOSED'].fillna(0)
prev_loans['PREV_CREDIT_SOLD'] = prev_loans['PREV_CREDIT_SOLD'].fillna(0)
prev_loans['PREV_CREDIT_BAD_DEBT'] = prev_loans['PREV_CREDIT_BAD_DEBT'].fillna(0)
prev_loans.head()

prev_loans.shape

prev_loans.dtypes

# Cek Missing Data
total_missing = prev_loans.isnull().sum().sort_values(ascending=False)
percent_1 = prev_loans.isnull().sum()/prev_loans.isnull().count()*100
percent_2 = (round(percent_1, 1)).sort_values(ascending=False)
missing_data = pd.concat([total_missing, percent_2], axis=1, keys=['Total Missing', '%'])
missing_data = missing_data.reset_index().rename(columns={'index': 'Column'})
missing_data

app_train = app_train.merge(prev_loans, on = 'SK_ID_CURR', how = 'left')

app_train.shape

"""#### Menambahkan fitur dari data previous application"""

prev_app = previous_application.groupby('SK_ID_CURR', as_index=False)['SK_ID_PREV'].count().rename(columns = {'SK_ID_PREV': 'PREV_APP_LOANS'})
prev_app.head()

# Total Credit Types setiap nasabah
xx = previous_application[['SK_ID_CURR','NAME_CONTRACT_TYPE']].groupby(by=['SK_ID_CURR'])['NAME_CONTRACT_TYPE'].nunique()
xx = xx.reset_index().rename(columns={'NAME_CONTRACT_TYPE':'PREV_APP_TOTAL_NAME_CONTRACT_TYPE'})
xx.head()

# Merge
prev_app = prev_app.merge(xx, on = 'SK_ID_CURR', how = 'left')
prev_app.head()

# rata - rata setiap tipe peminjaman
prev_app['PREV_APP_AVG_CONTRACT_TYPE'] = prev_app['PREV_APP_LOANS']/prev_app['PREV_APP_TOTAL_NAME_CONTRACT_TYPE']
prev_app.head()

# Modus dari prev Credit Types
xx = previous_application[['SK_ID_CURR','NAME_CONTRACT_TYPE']].groupby(by=['SK_ID_CURR'])['NAME_CONTRACT_TYPE'].agg(lambda x: scipy.stats.mode(x)[0]).str[0]
xx = xx.reset_index().rename(columns={'NAME_CONTRACT_TYPE':'PREV_APP_CONTRACT_TYPE_MODE'})
xx.head()

# Merge
prev_app = prev_app.merge(xx, on = 'SK_ID_CURR', how = 'left')
prev_app.head()

# Total Prev App Contract Status Approved
index = previous_application[
    (previous_application['NAME_CONTRACT_STATUS'] == 'Canceled') |
    (previous_application['NAME_CONTRACT_STATUS'] == 'Refused') |
    (previous_application['NAME_CONTRACT_STATUS'] == 'Unused offer')
].index

app_approve = previous_application.drop(index)

app_approve = app_approve[['SK_ID_CURR','NAME_CONTRACT_STATUS']].groupby(by=['SK_ID_CURR'])['NAME_CONTRACT_STATUS'].count()
app_approve = app_approve.reset_index().rename(columns={'NAME_CONTRACT_STATUS':'PREV_APP_CONTRACT_APPROVED'})
app_approve.head()

# Total Prev App Contract Status Canceled
index = previous_application[
    (previous_application['NAME_CONTRACT_STATUS'] == 'Approved') |
    (previous_application['NAME_CONTRACT_STATUS'] == 'Refused') |
    (previous_application['NAME_CONTRACT_STATUS'] == 'Unused offer')
].index

app_canceled = previous_application.drop(index)

app_canceled = app_canceled[['SK_ID_CURR','NAME_CONTRACT_STATUS']].groupby(by=['SK_ID_CURR'])['NAME_CONTRACT_STATUS'].count()
app_canceled = app_canceled.reset_index().rename(columns={'NAME_CONTRACT_STATUS':'PREV_APP_CONTRACT_CANCELED'})
app_canceled.head()

# Total Prev App Contract Status Refused
index = previous_application[
    (previous_application['NAME_CONTRACT_STATUS'] == 'Approved') |
    (previous_application['NAME_CONTRACT_STATUS'] == 'Canceled') |
    (previous_application['NAME_CONTRACT_STATUS'] == 'Unused offer')
].index

app_refused = previous_application.drop(index)

app_refused = app_refused[['SK_ID_CURR','NAME_CONTRACT_STATUS']].groupby(by=['SK_ID_CURR'])['NAME_CONTRACT_STATUS'].count()
app_refused = app_refused.reset_index().rename(columns={'NAME_CONTRACT_STATUS':'PREV_APP_CONTRACT_REFUSED'})
app_refused.head()

# Total Prev App Contract Status Unused Offer
index = previous_application[
    (previous_application['NAME_CONTRACT_STATUS'] == 'Approved') |
    (previous_application['NAME_CONTRACT_STATUS'] == 'Canceled') |
    (previous_application['NAME_CONTRACT_STATUS'] == 'Refused')
].index

app_uo = previous_application.drop(index)

app_uo = app_uo[['SK_ID_CURR','NAME_CONTRACT_STATUS']].groupby(by=['SK_ID_CURR'])['NAME_CONTRACT_STATUS'].count()
app_uo = app_uo.reset_index().rename(columns={'NAME_CONTRACT_STATUS':'PREV_APP_CONTRACT_UNUSED_OFFER'})
app_uo.head()

# Merge
prev_app = prev_app.merge(app_approve, on = 'SK_ID_CURR', how = 'left')
prev_app = prev_app.merge(app_canceled, on = 'SK_ID_CURR', how = 'left')
prev_app = prev_app.merge(app_refused, on = 'SK_ID_CURR', how = 'left')
prev_app = prev_app.merge(app_uo, on = 'SK_ID_CURR', how = 'left')
prev_app.head()

# isi data yang kosong
prev_app['PREV_APP_CONTRACT_APPROVED'] = prev_app['PREV_APP_CONTRACT_APPROVED'].fillna(0)
prev_app['PREV_APP_CONTRACT_CANCELED'] = prev_app['PREV_APP_CONTRACT_CANCELED'].fillna(0)
prev_app['PREV_APP_CONTRACT_REFUSED'] = prev_app['PREV_APP_CONTRACT_REFUSED'].fillna(0)
prev_app['PREV_APP_CONTRACT_UNUSED_OFFER'] = prev_app['PREV_APP_CONTRACT_UNUSED_OFFER'].fillna(0)
prev_app.head()

# Imputing XNA Value
prev_app['PREV_APP_CONTRACT_TYPE_MODE'] = prev_app['PREV_APP_CONTRACT_TYPE_MODE'].replace('XNA', 'Consumer loans')

# Simple Interest
total_payment = previous_application['AMT_ANNUITY'] * previous_application['CNT_PAYMENT']
prev_app['SIMPLE_INTEREST'] = (total_payment/previous_application['AMT_CREDIT'] - 1)/previous_application['CNT_PAYMENT']
prev_app.head()

# Fillna 0 Simple Interest
prev_app['SIMPLE_INTEREST'] = prev_app['SIMPLE_INTEREST'].fillna(0)

prev_app.shape

prev_app.dtypes

# Cek Missing Data
total_missing = prev_app.isnull().sum().sort_values(ascending=False)
percent_1 = prev_app.isnull().sum()/prev_app.isnull().count()*100
percent_2 = (round(percent_1, 1)).sort_values(ascending=False)
missing_data = pd.concat([total_missing, percent_2], axis=1, keys=['Total Missing', '%'])
missing_data = missing_data.reset_index().rename(columns={'index': 'Column'})
missing_data

# merge 2 dataframe dengan left join
app_train = app_train.merge(prev_app, on = 'SK_ID_CURR', how = 'left')

app_train.shape

"""#### Menambahkan fitur dari data POS Cash Balance"""

pos_cash_balance = pos_cash_balance.sort_values(by='SK_ID_CURR')
pos_cash_balance.head()

pcb_feature = pos_cash_balance.groupby('SK_ID_CURR', as_index=False)['MONTHS_BALANCE'].count().rename(columns = {'MONTHS_BALANCE': 'PCB_TOTAL_MONTH_BALANCE'})
pcb_feature.head()

pos_cash_balance['LATE_PAYMENT'] = pos_cash_balance['SK_DPD'].apply(lambda x:1 if x > 0 else 0)
pos_cash_balance.head()

month_late = pos_cash_balance[['SK_ID_CURR','LATE_PAYMENT']].groupby(by=['SK_ID_CURR'])['LATE_PAYMENT'].sum()
month_late = month_late.reset_index().rename(columns={'LATE_PAYMENT':'PCB_TOTAL_MONTH_LATE_PAYMENT'})
month_late.head()

# Merge 
pcb_feature = pcb_feature.merge(month_late, on = 'SK_ID_CURR', how = 'left')
pcb_feature.head()

pcb_feature.shape

pcb_feature.dtypes

# merge 2 dataframe dengan left join
app_train = app_train.merge(pcb_feature, on = 'SK_ID_CURR', how = 'left')

app_train.shape

"""### Cek dan Cleaning Data Training kembali"""

# Cek Missing Data
total_missing = app_train.isnull().sum().sort_values(ascending=False)
percent_1 = app_train.isnull().sum()/app_train.isnull().count()*100
percent_2 = (round(percent_1, 1)).sort_values(ascending=False)
missing_data = pd.concat([total_missing, percent_2], axis=1, keys=['Total Missing', '%'])
missing_data = missing_data.reset_index().rename(columns={'index': 'Column'})
missing_data

# Fill NA
for kolom in missing_data['Column']:
  if app_train[kolom].dtype == 'object':
    app_train[kolom] = app_train[kolom].fillna(app_train[kolom].mode()[0])
  else:
    app_train[kolom] = app_train[kolom].fillna(0)

app_train.replace([np.inf, -np.inf], 0, inplace=True)

"""Melakukan One Hot Encoding untuk merubah data kategorikal"""

# One Hot Encoding
cat_col = [category for category in app_train.columns if app_train[category].dtype == 'object']
app_train = pd.get_dummies(app_train, columns=cat_col)

app_train.shape

"""Hasil akhir dari Feature Engineering yaitu

Data train memiliki 179.793 data dengan 200 fitur

## Modeling
"""

# import libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, BaggingRegressor
from xgboost import XGBClassifier

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, roc_curve, auc, classification_report, roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

"""### Split Dataset

Saat melakukan Split dataset, digunakan stratify karena dataset yang digunakan memiliki target yang sangat imbalance.
"""

# Drop Target dan ID
X = app_train.drop(['SK_ID_CURR','TARGET'], axis=1)
Y = app_train.TARGET

# Split Dataset
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.3, random_state=1, stratify=Y)

print('Shape X_train : ', X_train.shape)
print('Shape X_test : ', X_test.shape)
print('Shape y_train : ', y_train.shape)
print('Shape y_test : ', y_test.shape)

"""### Pelatihan

#### Random Forest
"""

# Random Forest
rf_model = RandomForestClassifier(
    bootstrap=False, 
    criterion='entropy', 
    max_depth=16,
    n_estimators=200, 
    n_jobs=-1, 
    random_state=42
)

rf_model.fit(X_train.values,y_train.values.ravel())

"""#### Gradient Boosting"""

gb_model = GradientBoostingClassifier(
    loss='log_loss',
    criterion='friedman_mse', 
    max_depth=16,
    n_estimators=200, 
    random_state=42
)

gb_model.fit(X_train.values,y_train.values.ravel())

"""## Evaluasi

### Random Forest

Melakukan prediksi untuk X_test
"""

y_pred_rf = rf_model.predict_proba(X_test.values)[::,1]

"""Menggunakan Threshold berdasarkan ROC AUC karena data yang imbalance"""

fpr, tpr, thresholds = roc_curve(y_test, y_pred_rf)

plt.plot(fpr,tpr)
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()

# Calculate the Youden's J statistic
youdenJ = tpr - fpr

# Find the optimal threshold
index = np.argmax(youdenJ)
thresholdOpt = round(thresholds[index], ndigits = 4)
youdenJOpt = round(youdenJ[index], ndigits = 4)
fprOpt = round(fpr[index], ndigits = 4)
tprOpt = round(tpr[index], ndigits = 4)
print('Best Threshold: {} with Youden J statistic: {}'.format(thresholdOpt, youdenJOpt))
print('FPR: {}, TPR: {}'.format(fprOpt, tprOpt))

"""Melakukan konversi dari probabilitas menjadi target"""

y_pred_convert = y_pred_rf.copy()

for i in range(0, len(y_pred_convert)):
  if y_pred_convert[i] > thresholdOpt:
    y_pred_convert[i] = 1
  else:
    y_pred_convert[i] = 0

"""#### Hasil Evaluasi Random Forest"""

print("Accuracy Random Forest: ", accuracy_score(y_test, y_pred_convert))
print("Precision Random Forest: ", precision_score(y_test, y_pred_convert, average='macro'))
print("Recall Random Forest: ",recall_score(y_test, y_pred_convert, average='macro'))

score = roc_auc_score(y_test, y_pred_convert)

print(f"ROC AUC Random Forest: {score}")

f1_rf = f1_score(y_test, y_pred_convert)
print(f"F1 Score Random Forest: {f1_rf}")

# Confusion Matrix Random Forest
print("Cofusion Matrix Random Forest: \n", confusion_matrix(y_test, y_pred_convert))

"""### Gradient Boosting"""

y_pred_gb = gb_model.predict_proba(X_test.values)[::,1]

"""Menggunakan Threshold berdasarkan ROC AUC karena data yang imbalance"""

fpr, tpr, thresholds = roc_curve(y_test, y_pred_gb)

plt.plot(fpr,tpr)
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()

# Calculate the Youden's J statistic
youdenJ = tpr - fpr

# Find the optimal threshold
index = np.argmax(youdenJ)
thresholdOpt = round(thresholds[index], ndigits = 4)
youdenJOpt = round(youdenJ[index], ndigits = 4)
fprOpt = round(fpr[index], ndigits = 4)
tprOpt = round(tpr[index], ndigits = 4)
print('Best Threshold: {} with Youden J statistic: {}'.format(thresholdOpt, youdenJOpt))
print('FPR: {}, TPR: {}'.format(fprOpt, tprOpt))

"""Melakukan konversi dari probabilitas menjadi target"""

y_pred_convert = y_pred_gb.copy()

for i in range(0, len(y_pred_convert)):
  if y_pred_convert[i] > thresholdOpt:
    y_pred_convert[i] = 1
  else:
    y_pred_convert[i] = 0

"""#### Hasil Evaluasi Gradient Boosting"""

print("Accuracy Gradient Boosting: ", accuracy_score(y_test, y_pred_convert))
print("Precision Gradient Boosting: ", precision_score(y_test, y_pred_convert, average='macro'))
print("Recall Gradient Boosting: ",recall_score(y_test, y_pred_convert, average='macro'))

score = roc_auc_score(y_test, y_pred_convert)

print(f"ROC AUC Gradient Boosting: {score}")

f1_rf = f1_score(y_test, y_pred_convert)
print(f"F1 Score Gradient Boosting: {f1_rf}")

# Confusion Matrix Gradient Boosting
print("Cofusion Matrix Gradient Boosting: \n", confusion_matrix(y_test, y_pred_convert))