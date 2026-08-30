# Hacim Ağırlıklı MACD

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/vwmacd.md)

`zeonta.vwmacd()` — MACD built from Volume-Weighted Moving Averages instead of EMAs.

## Ne ölçer

[macd](macd.md) ile aynı hızlı-eksi-yavaş-sonra-sinyal şekli, ama düz bir EMA yerine [vwma](vwma.md)'dan inşa edilir. Hızlı ve yavaş çizgileri hacimle ağırlıklandırmak, kesişimleri düz MACD'nin yaptığı gibi ince, sakin bir barı yoğun işlem gören biriyle aynı kefeye koymak yerine, yoğun işlem gören hareketleri daha temsili hale getirir. Sinyal çizgisi düz bir EMA olarak kalır — MACD çizgisinin kendisi zaten hacim ağırlıklandırmasını taşır.

## Formül

```text
VWMACD = VWMA(fast) - VWMA(slow); Sinyal = EMA(VWMACD, signal); Histogram = VWMACD - Sinyal
```

## Parametreler

**Gerekli girdiler:** `close`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `fast` | `12` |
| `slow` | `26` |
| `signal` | `9` |

## Döndürdükleri

| Kolon |
| --- |
| `VWMACD_12_26_9` |
| `VWMACDs_12_26_9` |
| `VWMACDh_12_26_9` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vwmacd(df['close'], df['volume']).tail(3)
```

```text
            VWMACD_12_26_9  VWMACDs_12_26_9  VWMACDh_12_26_9
date                                                        
2024-10-25       -0.220966        -0.248308         0.027342
2024-10-26       -0.261812        -0.251009        -0.010803
2024-10-27       -0.426664        -0.286140        -0.140524
```

**Accessor biçimi:** `df.zta.vwmacd(...)`

## Nasıl okunur

Tam olarak `macd` gibi okunur — çizgi ile kendi sinyali arasındaki kesişim, ya da çizginin sıfırı kesmesi.

## Dikkat edilmesi gerekenler

`vwma`'nın kendi sıfır-toplam-hacim uç durumunu miras alır: bir pencerenin toplam hacminin tam olarak `0` olduğu her yerde `NaN` olur.

## Kaynak

Formül kaynağı: [https://vectoralpha.dev/projects/ta/indicators/vwmacd/](https://vectoralpha.dev/projects/ta/indicators/vwmacd/)
