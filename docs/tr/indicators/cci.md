# Emtia Kanal Endeksi (CCI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/cci.md)

`zeonta.cci()` — How far typical price has strayed from its own average, in mean deviations.

## Ne ölçer

CCI, tipik fiyatın kendi ortalamasından ne kadar uzaklaştığını, o dönemin normal sapması cinsinden ölçer. Adına rağmen özellikle emtialarla bir ilgisi yoktur — her şey üzerinde çalışır.

## Formül

```text
TP = (En Yüksek + En Düşük + Kapanış) / 3; CCI = (TP - HO(TP, 20)) / (0.015 x OrtalamaSapma(TP, 20))
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |
| `constant` | `0.015` |

## Döndürdükleri

| Kolon |
| --- |
| `CCI_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cci(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    -60.651903
2024-10-26   -131.135840
2024-10-27   -176.160519
Name: CCI_20, dtype: float64
```

**Accessor biçimi:** `df.zta.cci(...)`

## Nasıl okunur

0,015 sabiti, okumaların kabaca %70-80'inin -100 ile +100 arasında kalması için seçilmiştir. Bu bandın dışına çıkan hareketler olağandışı bir sapmayı işaret eder: ya tükenmiş bir uç nokta, ya da trend takibi okumasında katılmaya değer bir kırılım.

## Dikkat edilmesi gerekenler

CCI sınırsızdır, dolayısıyla "+100 aşırı alımdır" bir tavan değil, bir gelenektir — güçlü trendler rutin olarak +300 basar. İki standart yorum (uç noktayı ters yönde kullanmak ya da kırılımı takip etmek) birbirinin zıddıdır; işlem yapmadan önce hangisini kullandığınıza karar verin.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/cci](https://ta.cognicode.org/learn/cci)
