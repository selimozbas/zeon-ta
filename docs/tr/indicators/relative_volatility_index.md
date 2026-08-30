# Göreceli Oynaklık Endeksi (RVI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/relative_volatility_index.md)

`zeonta.relative_volatility_index()` — RSI's up/down split applied to standard deviation instead of price change.

## Ne ölçer

Donald Dorsey'in oynaklığa [rsi](rsi.md) şeklindeki yaklaşımı: Wilder'ın fiyat değişimi için kullandığı aynı yukarı/aşağı-ayır-sonra-yumuşat yapısı, bunun yerine yuvarlanan bir standart sapmaya uygulanır — [atr](atr.md)'den farklı olarak, *yönü* olan bir oynaklık ölçüsü.

## Formül

```text
SD = STDDEV(Kapanış, stdev_length); U/D = SD, yukarı/aşağı kapanışa göre ayrılır; RVI = 100 * EMA(U) / (EMA(U) + EMA(D))
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `stdev_length` | `10` |
| `smooth_length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `RVI_10_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.relative_volatility_index(df['close']).tail(3)
```

```text
date
2024-10-25    37.835098
2024-10-26    32.714115
2024-10-27    27.861198
Name: RVI_10_14, dtype: float64
```

**Accessor biçimi:** `df.zta.relative_volatility_index(...)`

## Nasıl okunur

50'nin üstü, son oynaklığın aşağı barlardan çok yukarı barlarda ortaya çıktığı anlamına gelir; 50'nin altı ise tersidir. Genellikle bir trend indikatörüyle eşleştirilir: doğrulanmış bir yükseliş trendiyle birlikte yükselen RVI hareketi destekler, trende karşı yükselen RVI ise olası bir dönüşe karşı uyarır.

## Dikkat edilmesi gerekenler

`rsi`'nin ihtiyaç duyduğu tek periyot yerine, üst üste iki periyot (`stdev_length`, `smooth_length`) — ikisi de sonucu anlamlı şekilde değiştirir.

## Kaynak

Formül kaynağı: [https://user42.tuxfamily.org/chart/manual/Relative-Volatility-Index.html](https://user42.tuxfamily.org/chart/manual/Relative-Volatility-Index.html)
