# Ichimoku

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ichimoku.md)

`zeonta.ichimoku()` — Five-line Japanese system giving trend, momentum and support in one view.

## Ne ölçer

Tek bir gösterge değil, eksiksiz bir sistem: aralarında trendi, momentumu, destek ve direnci tek bakışta veren beş çizgi. İki Senkou span'i arasındaki bulut 26 bar ileriye yansıtılır; Ichimoku'yu bir grafikteki her şeyden farklı gösteren de budur.

## Formül

```text
Tenkan-sen = (En Yüksek(9) + En Düşük(9)) / 2; Kijun-sen = (En Yüksek(26) + En Düşük(26)) / 2; Senkou Span A = (Tenkan-sen + Kijun-sen) / 2, 26 periyot ileriye çizilir; Senkou Span B = (En Yüksek(52) + En Düşük(52)) / 2, 26 periyot ileriye çizilir; Chikou Span = Kapanış, 26 periyot geriye çizilir
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `tenkan` | `9` |
| `kijun` | `26` |
| `senkou` | `52` |
| `displacement` | `26` |

## Döndürdükleri

| Kolon |
| --- |
| `ITS_9` |
| `IKS_26` |
| `ISA_9_26` |
| `ISB_52` |
| `ICS_26` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ichimoku(df['high'], df['low'], df['close'])[0].tail(2)
```

```text
               ITS_9    IKS_26   ISA_9_26    ISB_52  ICS_26
date                                                       
2024-10-26  90.52465  90.94945  91.997300  92.92670     NaN
2024-10-27  89.85265  90.52225  91.869125  92.79215     NaN
```

```python
zeonta.ichimoku(df['high'], df['low'], df['close'])[1].head(2)
```

```text
             ISA_9_26    ISB_52
2024-10-28  91.869125  92.79215
2024-10-29  91.869125  92.79215
```

**Accessor biçimi:** `df.zta.ichimoku(...)`

## Nasıl okunur

Bulutun üstündeki fiyat boğa, altındaki ayı, içindeki ise kararsız yöndedir. Kalın bulut güçlü destek ya da dirençtir; ince bulut kolayca kesilir. Bu fonksiyon iki tablo döndürür — grafik üzerindeki çizgiler ve bulutun son barın ötesine düşen kısmı.

## Dikkat edilmesi gerekenler

İleri bulut bir tahmin değildir: bugünün orta noktalarının 26 bar sağa çizilmiş hâlidir ve oraya varıldığında değişmeyecektir. Ayrıca varsayılan 9/26/52 ayarları altı günlük Japon işlem haftasından gelir; beş günlük ya da 7/24 açık bir piyasada özel bir anlam taşımaz.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/ichimoku](https://ta.cognicode.org/learn/ichimoku)
