# SEM-EDS（地惑のFE-SEM）の画像＆エネルギースペクトルを、画像ごとに整理したPDFを作る。

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.lib.utils import ImageReader
from io import BytesIO
import glob
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as plc
import matplotlib.ticker as tic
from matplotlib import rcParams
from tqdm import tqdm


pdf_title = "Report.pdf"

paper = canvas.Canvas(pdf_title)
paper.saveState()
paper.setPageSize((210*mm, 297*mm))

plt.rcParams["font.family"] = "Arial"
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.linewidth"] = 7
plt.rcParams["xtick.labelsize"] = 30
plt.rcParams["ytick.labelsize"] = 30
plt.rcParams["xtick.direction"] = "out"
plt.rcParams["ytick.direction"] = "out"
plt.rcParams["xtick.major.size"] = 12
plt.rcParams["ytick.major.size"] = 12
plt.rcParams["xtick.minor.size"] = 8
plt.rcParams["ytick.minor.size"] = 8
plt.rcParams["xtick.major.pad"] = 5
plt.rcParams["ytick.major.pad"] = 5
plt.rcParams["xtick.minor.pad"] = 3
plt.rcParams["ytick.minor.pad"] = 3
plt.rcParams["xtick.major.width"] = 7
plt.rcParams["ytick.major.width"] = 7
plt.rcParams["xtick.minor.width"] = 5
plt.rcParams["ytick.minor.width"] = 5


# 画像の検索・整理
photo_list = glob.glob("EDS/画像/*_marker.bmp")
photo_num = []
for i in photo_list:
    photo_num.append(i[-14:-11])
photo_num_sorted = sorted(photo_num)
print("{} pictures".format(len(photo_num_sorted)))

all_photo = glob.glob("EDS/画像/*.bmp")
all_photo_sorted = []
for i in photo_num_sorted:
    all_photo_sorted_i = []
    for j in all_photo:
        if i in j:
            all_photo_sorted_i.append(j)
    all_photo_sorted.append(all_photo_sorted_i)
#print(all_photo_sorted)


# csvと画像の照合
csv_list = glob.glob("EDS/csv/*.csv")
csv_num = []
for i in csv_list:
    csv_num.append(i[-11:-4])
csv_num_sorted = sorted(csv_num)

csv_sorted = []  # csvを順番に並べ替え
for i in csv_num_sorted:
    for j in csv_list:
        if (j[-11:-4] == i):
            csv_sorted.append(j)

csv_grouped = []
for i in photo_num_sorted:  # 画像と対応するcsvをグループ分け
    csv_grouped_i = []
    for j in csv_sorted:
        if j[10:13] == i:
            csv_grouped_i.append(j)
    csv_grouped.append(csv_grouped_i)
#print(csv_grouped)


page_num = 0

#for i in tqdm([['EDS/画像/allende_018_marker.bmp'], ['EDS/画像/Allende_114_marker.bmp','EDS/画像/Allende_114.bmp']]):
for i in tqdm(all_photo_sorted):  # 写真の数だけサイクル
    for j in range(0, len(photo_num_sorted)):
        create_new_page = 0
        for item in i:
            if "{}.bmp".format(photo_num_sorted[j]) in item:
                paper.drawInlineImage(item, 25*mm, 220*mm, 1024*0.2, 768*0.2)
                sample_name = item.replace("EDS/画像/", "")
                sample_name = sample_name.replace("_{}.bmp".format(photo_num_sorted[j]), "")
                create_new_page = create_new_page+1
            if "{}_marker.bmp".format(photo_num_sorted[j]) in item:
                paper.drawInlineImage(item, 105*mm, 217*mm, 512*0.42, 406*0.4)
                sample_name = item.replace("EDS/画像/", "")
                sample_name = sample_name.replace("_{}_marker.bmp".format(photo_num_sorted[j]), "")
                create_new_page = create_new_page+1

        if create_new_page != 0:  # 以下、EDSスペクトルを追加

            total_page_fig = np.ceil(len(csv_grouped[j]) / 10)
            page_fig = 0
            k = 0

            while True:

                paper.drawString(25*mm, 280*mm, "Sample: {} (photo #{}) {}/{}".format(sample_name, photo_num_sorted[j], k+1, int(total_page_fig)))
                page_num = page_num + 1
                paper.drawString(175*mm, 280*mm, "p.{}".format(page_num))

                residue = len(csv_grouped[j]) - 10 * page_fig
                if residue >= 10:
                    fig_num = 10
                if residue < 10:
                    fig_num = residue

                fig1 = plt.figure(figsize = (25, 6.25 * np.ceil(fig_num/2)), linewidth=7, tight_layout=True)

                while True:

                    df_i = pd.read_csv(csv_grouped[j][k+10*page_fig], low_memory=True)
                    energy = df_i["Energy[keV]"].astype(float)
                    count = df_i["Count"].astype(float)

                    ax1 = fig1.add_subplot(np.ceil((fig_num)/2), 2, k+1)
                    ax1.plot(energy, count, marker="None", ls="-", lw=5, color="black", label=k+10*page_fig+1)
                    ax1.set_xlim(0, 12)
                    #ax1.set_ylim(0, 1000)
                    #ax1.get_xaxis().set_major_locator(tic.MultipleLocator(500))
                    #ax1.get_xaxis().set_minor_locator(tic.MultipleLocator(100))
                    #ax1.get_yaxis().set_major_locator(tic.MultipleLocator(10))
                    #ax1.get_yaxis().set_minor_locator(tic.MultipleLocator(2))
                    ax1.set_xlabel("Energy / keV", fontsize=30, fontname="Arial", fontweight="bold")
                    ax1.set_ylabel("Signal Intensity / counts", fontsize=30, fontname="Arial", fontweight="bold")
                    ax1.grid()
                    ax1.legend(fontsize=40, loc="upper right")
                    ax1.set_axisbelow(True)

                    imgdata = BytesIO()
                    fig1.savefig(imgdata, format="png")
                    imgdata.seek(0)  # rewind the data

                    Image = ImageReader(imgdata)
                    paper.drawImage(Image, 25*mm, 297*mm-80*mm-40*np.ceil(fig_num/2)*mm, 440, 105*np.ceil(fig_num/2))
                    plt.close()

                    k = k + 1
                    if k == fig_num:
                        page_fig = page_fig + 1
                        k = 0
                        paper.showPage()
                        break

                if page_fig == total_page_fig:
                    break

paper.save()
