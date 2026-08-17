# Stokastik Osilatör

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/stoch.md)

`zeonta.stoch()` — Where the close sits inside the recent high-low range.

## Ne ölçer

Bu bar, son dönem aralığının neresinde kapandı — tepesinde mi, dibinde mi, ortasında mı? Fikrin tamamı bu. Son n barın zirvelerine yakın kapanış 100'e yakın puan alır; diplere yakın kapanış 0'a yakın.

## Formül

```text
%K = 100 x (Kapanış - EnDüşük(n)) / (EnYüksek(n) - EnDüşük(n)); %K(yumuşatılmış) = HO(%K, smoothK); %D = HO(%K yumuşatılmış, smoothD)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |
| `smooth_k` | `3` |
| `smooth_d` | `3` |

## Döndürdükleri

| Kolon |
| --- |
| `STOCHk_14_3_3` |
| `STOCHd_14_3_3` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.stoch(df['high'], df['low'], df['close']).tail(3)
```

```text
            STOCHk_14_3_3  STOCHd_14_3_3
date                                    
2024-10-25      37.289365      31.251025
2024-10-26      24.223173      31.328924
2024-10-27      14.007530      25.173356
```

**Accessor biçimi:** `df.zta.stoch(...)`

## Nasıl okunur

80'in üstü kapanışların aralığın tepesinde kümelendiğini, 20'nin altı ise dibinde kümelendiğini gösterir. `%D` çizgisi yumuşatılmış sinyaldir; `%K`'nin düşük bir seviyeden `%D`'nin üstüne çıkması klasik uzun pozisyon tetikleyicisidir.

## Dikkat edilmesi gerekenler

Stokastik yatay bantlar için tasarlanmıştır ve trendde doyuma ulaşır: güçlü bir yükselişin tamamı boyunca 100'e yapışır ve bir dizi erken satış sinyali üretir. Uç değerlere göre işlem yapmadan önce ADX gibi bir trend ölçüsüyle filtreleyin.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/stochastic](https://ta.cognicode.org/learn/stochastic)
