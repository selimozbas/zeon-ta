# Aroon ve Aroon Osilatörü

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/aroon.md)

`zeonta.aroon()` — How recently price made a new high vs. a new low, as a 0-100 pair.

## Ne ölçer

`donchian` n-bar en yüksek ve en düşüğün fiyat açısından *nerede* olduğunu işaretlerken, Aroon bunların *ne kadar önce* olduğunu işaretler. Taze bir zirve, fiyat açısından ne kadar uzakta olursa olsun Aroon-Yukarı'yı 100 yapar; `n` bar önceki bir zirve ise fiyat hâlâ hemen yanında bile olsa 0 yapar — göstergenin tamamı seviyeyle değil, yakın zamanlılıkla ilgilidir.

## Formül

```text
Aroon-Yukarı = ((n - EnYüksekZirveÜzerindenGeçenGün) / n) x 100; Aroon-Aşağı = ((n - EnDüşükDipÜzerindenGeçenGün) / n) x 100; Aroon Osilatörü = Aroon-Yukarı - Aroon-Aşağı
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `25` |

## Döndürdükleri

| Kolon |
| --- |
| `AROONU_25` |
| `AROOND_25` |
| `AROONOSC_25` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.aroon(df['high'], df['low']).tail(3)
```

```text
            AROONU_25  AROOND_25  AROONOSC_25
date                                         
2024-10-25       64.0       92.0        -28.0
2024-10-26       60.0       88.0        -28.0
2024-10-27       56.0      100.0        -44.0
```

**Accessor biçimi:** `df.zta.aroon(...)`

## Nasıl okunur

Aroon-Yukarı 70'in üstünde ve Aroon-Aşağı 30'un altındayken güçlü bir yükseliş trendi işaret eder (zirveler yenilenmeye devam ediyor, dipler eskimiş); ayna görüntüsü bir düşüş trendini işaret eder. Aroon Osilatörü ikisini sıfır etrafında tek bir çizgide birleştirir: sürekli pozitif okumalar yükseliş eğilimini, sürekli negatif okumalar düşüş eğilimini işaret eder.

## Dikkat edilmesi gerekenler

Aroon-Yukarı ve Aroon-Aşağı aynı anda hem yüksek hem düşük olabilir (dalgalı bir piyasa aynı pencerede hem taze zirve hem taze dip yapabilir); osilatör tek başına bunları birbirinden çıkararak gizler — trend olmadığı sonucuna varmadan önce sadece osilatöre değil, iki ham çizgiye de bakın. Pencere içindeki uç değer eşitlikleri, kaynağın kendi kuralına uygun olarak en son gerçekleşen lehine çözülür.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon)
