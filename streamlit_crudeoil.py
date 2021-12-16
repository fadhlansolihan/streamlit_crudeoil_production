import streamlit as st
import pandas as pd

# Container yang ada di program ini
header = st.container()
tahun_minyak =  st.expander("Jumlah Produksi Minyak Mentah Negara per Tahun", expanded=False)
rank_kumulatif = st.expander("Negara Produsen Minyak Terbesar", expanded=False)
rank_tahun = st.expander("Negara Produsen Minyak Terbesar per Tahun", expanded=False)
negara_filter = st.expander("Filter Negara Berdasarkan Produksi Minyak", expanded=False)

# Baca data dan assign ke sebuah variabel untuk membentuk objek
df = pd.read_csv('produksi_minyak_mentah.csv', index_col="kode_negara")
df_neg = pd.read_json("kode_negara_lengkap.json")

# Hilangkan dari list negara yang bukan merupakan negara
alpha3List = df_neg['alpha-3'].tolist()
for alpha3 in df.index.unique().tolist():
    if alpha3 not in alpha3List:
        df.drop([alpha3], inplace=True)
df.reset_index(inplace=True)

# Buat list negara tanpa duplikat (untuk entry di dropdown menu di bagian jumlah produksi minyak mentah negara per tahun)
list_negara = [(df_neg.loc[df_neg['alpha-3'] == negara].values[0][0]) for negara in df['kode_negara'].unique().tolist()]

# Menuliskan data negara satu per satu dari parameter yang diberikan menjadi markdown
def show_negara(nama, alpha3, region, subregion, total_prod, tertinggi_sum=None, tertinggi_tahun=None):
    st.markdown(f'Nama: **{nama}**')
    st.markdown(f'Kode: **{alpha3}**')
    st.markdown(f'Region: **{region}**')
    st.markdown(f'Subregion: **{subregion}**')
    st.markdown(f'Total produksi: **{total_prod}**')
    if tertinggi_sum==None and tertinggi_tahun==None:
        return
    st.markdown(f'Dengan produksi tahunan tertinggi: **{tertinggi_sum}** pada tahun **{tertinggi_tahun}**')

# Memasukkan data ke sebuah tabel dan kemudian menampilkannya
def show_table(nama, alpha3, region, subregion, total_prod):
    f_table = pd.DataFrame()
    f_table['Nama'] = f_table.append({'Nama':nama}, ignore_index=True)
    f_table['Kode'] = alpha3
    f_table['Region'] = region
    f_table['Subregion'] = subregion
    f_table['Produksi'] = total_prod
    st.dataframe(f_table)

# Header
with header:
    st.markdown("# PetroCount.")
    st.info("*PetroCount.* adalah aplikasi yang dapat digunakan untuk menghitung data produksi minyak untuk seluruh negara di dunia.")
    st.image('offshore.jpg')
    st.markdown("***")

# graph minyak negara
with tahun_minyak:
    # Input user
    selectNegara = st.selectbox("Pilih Negara", list_negara)
    # Cari kode negara
    alpha3Negara = df_neg[df_neg["name"] == selectNegara]["alpha-3"].values[0]
    st.write(f'{selectNegara} ({alpha3Negara})')
    # Cari data yang negaranya sesuai kemudian ambil tahun dan jumlah produksinya
    display_data = df[df["kode_negara"] == alpha3Negara][['tahun', 'produksi']].rename(columns={'tahun':'index'}).set_index('index')
    # Tampilkan data
    st.bar_chart(display_data)

# rank negara tahunan
with rank_tahun:
    # input user
    t_inp = st.slider('Tahun Produksi', min_value=1971, max_value=2020, value=1971, step=1)
    n_inp = st.slider('Banyak Ranking', 1, len(list_negara), value=10, step=1)
    # cari data yang tahunnya sesuai kemudian disortir dari atas ke bawha
    tahun = df.loc[df["tahun"] == int(t_inp)].sort_values(["produksi"],ascending=[0])[:n_inp].reset_index(drop=True)
    tahun_out = tahun[['kode_negara', 'produksi']].rename(columns={'kode_negara':'index'}).set_index('index')
    # Tampilkan data
    st.bar_chart(tahun_out)

# rank negara kumulatif
with rank_kumulatif:
    # input user
    n_inp = st.slider('Banyak Ranking Negara', 1, len(list_negara), value=10, step=1)
    # grup data berdasarkan kode negara kemudian jumlahkan semua produksinya dan sortir dari atas ke bawah
    prod_sum = df[['kode_negara', 'produksi']].groupby('kode_negara', as_index=False).sum().sort_values(['produksi'], ascending=[0]).reset_index(drop=True)[:int(n_inp)].reset_index(drop=True)
    prod_sum_out = prod_sum[['kode_negara', 'produksi']].rename(columns={'kode_negara':'index'}).set_index('index')
    # tampilkan data
    st.bar_chart(prod_sum_out)


with negara_filter:
    # input user
    filter = st.radio('Filter', ['Tertinggi', 'Terkecil', 'Nol'])
    waktu = st.radio('Jangka Waktu', ['Semua', 'Tahun'])
    if filter == 'Tertinggi':
        if waktu == 'Tahun':
            # input user
            t_inp = st.slider('Tahun Produksi Maksimum', min_value=1971, max_value=2020, value=1971, step=1)
            # cari data yang tahunnya sesuai, kemudian ambil maksimum dari jumlah produksinya
            df_max_id = df[df['tahun'] == t_inp]['produksi'].idxmax()
            nTMax = df[df_max_id:df_max_id+1]
            kode, _, prod = nTMax.values.tolist()[0]
            # masukkan data satu per satu ke sebuah variabel
            nama = df_neg[df_neg["alpha-3"] == kode]["name"].values[0]
            reg = df_neg[df_neg["name"] == nama]["region"].values[0]
            subreg = df_neg[df_neg["name"] == nama]["sub-region"].values[0]
            st.markdown(f'#### Negara Produksi Tertinggi pada Tahun {t_inp}')
            # tampilkan data
            show_table(nama, kode, reg, subreg, prod)
        elif waktu == 'Semua':
            # cari nilai produksi tertinggi
            df_max_id = df['produksi'].idxmax()
            nMax = df[df_max_id:df_max_id+1]
            kode, _, prod = nMax.values.tolist()[0]
            # masukkan data satu per satu ke sebuah variabel
            nama = df_neg[df_neg["alpha-3"] == kode]["name"].values[0]
            reg = df_neg[df_neg["name"] == nama]["region"].values[0]
            subreg = df_neg[df_neg["name"] == nama]["sub-region"].values[0]
            st.markdown(f'#### Negara Produksi Tertinggi di Semua Waktu')
            # tampilkan data
            show_table(nama, kode, reg, subreg, prod)
    elif filter == 'Terkecil':
        if waktu == 'Tahun':
            try:
                # input user
                t_inp = st.slider('Tahun Produksi Minimum', min_value=1971, max_value=2020, value=1971)
                # cari data yang tahunnya sesuai dengan input user
                df_min_t = df[df['tahun'] == t_inp]
                # Ambil data apabila produksinya tidak nol
                df_min_t = df_min_t[df_min_t['produksi'] != 0]
                # cari nilai minimum
                df_min_id = df_min_t['produksi'].idxmin()
                print(df_min_t)
                kode, _, prod = df[df_min_id:df_min_id+1].values.tolist()[0]
                # masukkan data satu per satu ke sebuah variabel
                nama = df_neg[df_neg["alpha-3"] == kode]["name"].values[0]
                reg = df_neg[df_neg["name"] == nama]["region"].values[0]
                subreg = df_neg[df_neg["name"] == nama]["sub-region"].values[0]
                st.markdown(f'#### Negara Produksi Paling Rendah pada Tahun {t_inp}')
                # tampilkan data
                show_table(nama, kode, reg, subreg, prod)
            except Exception:
                st.error('Data tidak ditemukan')
        elif waktu == 'Semua':
            # ambil data yang nilai produksinya lebih dari nol
            df_min_t = (df[df['produksi'] > 0])
            df_min_t.reset_index(inplace=True)
            # cari nilai produksi minimumnya
            df_min_id = df_min_t['produksi'].idxmin()
            _, kode, _, prod = df_min_t[df_min_id:df_min_id+1].values.tolist()[0]
            # masukkan data satu per satu ke sebuah variabel
            nama = df_neg[df_neg["alpha-3"] == kode]["name"].values[0]
            reg = df_neg[df_neg["name"] == nama]["region"].values[0]
            subreg = df_neg[df_neg["name"] == nama]["sub-region"].values[0]
            st.markdown(f'#### Negara Produksi Paling Rendah di Semua Waktu')
            # tampilkan data
            show_table(nama, kode, reg, subreg, prod)

    elif filter == 'Nol':
        # cari data yang nilai produksinya nol
        df0_prod= df[df['produksi'] == 0]
        df0_prod.reset_index(inplace=True)
        nama = []
        region = []
        subregion = []
        for _, row in df0_prod.iterrows():
            # Iterasi dataset yang telah di filter 0 untuk mengappend tiap row dengan kode negara sebagai index
            kode = row['kode_negara']
            nama.append(df_neg[df_neg['alpha-3'] == kode]['name'].values[0])
            region.append(df_neg[df_neg['alpha-3'] == kode]['region'].values[0])
            subregion.append(df_neg[df_neg['alpha-3'] == kode]['sub-region'].values[0])
        df0_prod['Nama'] = nama
        df0_prod['Region'] = region
        df0_prod['Subregion'] = subregion
        if waktu == 'Tahun':
            # input user
            t_inp = st.slider('Tahun Produksi Kosong', min_value=1971, max_value=2020, value=1972)
            # cari data yang tahunnya sesuai dengan input user
            df0_showF = df0_prod[df0_prod['tahun'] == int(t_inp)]
            df0_showF.reset_index(inplace=True)
            # tampilkan data
            st.dataframe(df0_showF.filter(items=['Nama', 'kode_negara', 'Region', 'Subregion']))
        elif waktu == 'Semua':
            # tampilkan data
            st.dataframe(df0_prod.filter(items=['Nama', 'kode_negara', 'Region', 'Subregion']).drop_duplicates().drop(index=0).reset_index(drop=True))

st.caption("Muhammad Fadhlan Solihan - 12220071")