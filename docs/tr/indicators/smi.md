# Stokastik Momentum Endeksi (SMI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/smi.md)

`zeonta.smi()` — Double-smoothed stochastic that measures distance from the range's midpoint.

## Ne ölçer

William Blau'nun [stoch](stoch.md)'a getirdiği iyileştirme: kapanışın yüksek-düşük aralığının *içinde* nerede oturduğunu ölçmek yerine (0 ile 100 arası), kapanışın aralığın *orta noktasından* uzaklığını ölçer, sonra bölmeden önce hem bu uzaklığı hem de aralığın kendisini iki EMA geçişiyle çift-yumuşatır.

## Formül

```text
Orta = (EY+ED)/2; SMI = 200 * EMA(EMA(Kapanış-Orta,fast),slow) / EMA(EMA(EY-ED,fast),slow)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |
| `fast` | `3` |
| `slow` | `3` |
| `signal_length` | `3` |

## Döndürdükleri

| Kolon |
| --- |
| `SMI_10_3_3` |
| `SMIs_10_3_3` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.smi(df['high'], df['low'], df['close']).tail(3)
```

```text
            SMI_10_3_3  SMIs_10_3_3
date                               
2024-10-25  -37.061631   -38.831674
2024-10-26  -49.537086   -44.184380
2024-10-27  -60.390672   -52.287526
```

**Accessor biçimi:** `df.zta.smi(...)`

## Nasıl okunur

Sıradan bir stokastikle aynı aşırı-alım/aşırı-satım sezgisi (+40 üstü / -40 altı okumalar yaygın olarak belirtilir), ama hem pay hem payda çift-yumuşatıldığı için, SMI -100/+100 sınırlarına %K'nın yaptığından çok daha az ani şekilde ulaşır.

## Dikkat edilmesi gerekenler

Üç ayrı yumuşatma periyodu (aralık için `length`, iki EMA geçişi için `fast` ve `slow`) üst üste yığılır, bu yüzden etkin gecikme bunlardan herhangi birinin tek başına ima ettiğinden daha uzundur.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000589925-stochastic-momentum-index/](https://www.tradingview.com/support/solutions/43000589925-stochastic-momentum-index/)
