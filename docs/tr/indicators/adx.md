# ADX / DMI

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/adx.md)

`zeonta.adx()` — Wilder's directional movement system: trend strength (ADX) and direction (DI).

## Ne ölçer

Wilder'ın, çoğu göstergenin kaçındığı bir soruya cevabı: burada gerçekten bir trend var mı? ADX, yönü umursamadan trend gücünü ölçer; yönü ise +DI/-DI çifti ayrıca verir.

## Formül

```text
+DM = yukarı hareket, aşağı hareketi aşıyor ve pozitifse yukarı hareket, aksi halde 0; -DM = aşağı hareket, yukarı hareketi aşıyor ve pozitifse aşağı hareket, aksi halde 0; +DI = 100 x WilderYumuşatma(+DM, periyot) / ATR(periyot); -DI = 100 x WilderYumuşatma(-DM, periyot) / ATR(periyot); DX = 100 x |+DI - -DI| / (+DI + -DI); ADX = WilderYumuşatma(DX, periyot)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `ADX_14` |
| `DMP_14` |
| `DMN_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.adx(df['high'], df['low'], df['close'], length=14).tail(3)
```

```text
               ADX_14     DMP_14     DMN_14
date                                       
2024-10-25  15.703691  16.436469  22.152539
2024-10-26  16.249237  15.310359  24.633880
2024-10-27  17.531395  13.906973  28.363100
```

**Accessor biçimi:** `df.zta.adx(...)`

## Nasıl okunur

20'nin altındaki değerler kullanılabilir bir trend olmadığını, 25'in üstü takip etmeye değer bir trendi, 40'ın üstü ise güçlü bir trendi gösterir. Yönü hangi DI çizgisinin üstte olduğu söyler: `DMP`'nin `DMN` üstünde olması yükseliş trendidir. ADX, yatay bantlarda bozulan göstergeler için klasik filtredir.

## Dikkat edilmesi gerekenler

Düşüş trendinde yükselen bir ADX yine de yükselen bir ADX'tir — asla "boğa" demez. Zaten yumuşatılmış bir seriyi tekrar yumuşattığı için değer üretmeye başlamadan önce kabaca `2 x length` bara ihtiyaç duyar ve yapısı gereği geç döner.
