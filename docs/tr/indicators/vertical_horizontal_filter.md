# Dikey Yatay Filtre (VHF)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/vertical_horizontal_filter.md)

`zeonta.vertical_horizontal_filter()` — How much of a window's net move survived versus how much back-and-forth it took.

## Ne ölçer

Adam White'ın [choppiness_index](choppiness_index.md)'in yaptığı aynı karşılaştırmanın tersten kurulmuş ve ters yönde okunan versiyonu: pay ('dikey' hareket), pencerenin kapanış aralığının kat ettiği net mesafedir; payda ('yatay' hareket) ise oraya varmak için gereken toplam bar-başı mesafedir.

## Formül

```text
VHF = (EnYüksekKapanış(n) - EnDüşükKapanış(n)) / Toplam(|Kapanış[i] - Kapanış[i-1]|, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `28` |

## Döndürdükleri

| Kolon |
| --- |
| `VHF_28` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vertical_horizontal_filter(df['close']).tail(3)
```

```text
date
2024-10-25    0.214621
2024-10-26    0.237501
2024-10-27    0.272314
Name: VHF_28, dtype: float64
```

**Accessor biçimi:** `df.zta.vertical_horizontal_filter(...)`

## Nasıl okunur

Daha yüksek olması daha fazla trend anlamına gelir (benzer kuruluma rağmen CHOP'un tersi yönde) — pencerenin başından sonuna kadar az boşa giden hareket. Daha düşük olması daha fazla yalancı sinyal anlamına gelir: az net ilerleme için kat edilen çok fazla bar-başı mesafe.

## Dikkat edilmesi gerekenler

Pencerenin bar-başı hareketi tam olarak `0`'a toplandığında (tamamen düz bir pencere), tanımsız bir bölüm yerine `NaN` olur.

## Kaynak

Formül kaynağı: [https://www.rdocumentation.org/packages/TTR/versions/0.24.4/topics/VHF](https://www.rdocumentation.org/packages/TTR/versions/0.24.4/topics/VHF)
