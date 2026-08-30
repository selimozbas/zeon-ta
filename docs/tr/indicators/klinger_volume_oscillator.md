# Klinger Hacim Osilatörü (KVO)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/klinger_volume_oscillator.md)

`zeonta.klinger_volume_oscillator()` — Difference of two EMAs of a trend-and-range-scaled volume force.

## Ne ölçer

Stephen Klinger'ın [obv](obv.md)'nin daha kademeli kuzeni: bir barın tüm hacmini yalnızca yöne göre ekleyip çıkarmak yerine, 'hacim gücü', barın kendi aralığının trendin son değiştiğinden beri birikmiş aralığa göre nasıl karşılaştırıldığına göre ölçeklendirilir — yarım yürekli bir itiş, aralığın tüm harekete hakim olduğu bir bardan daha az katkı sağlar.

## Formül

```text
VF = 100 * Hacim * Trend * |2*(dm/cm) - 1|, dm = Yüksek-Düşük, cm, trendin son değiştiğinden beri dm'yi biriktirir; KVO = EMA(VF,fast) - EMA(VF,slow)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `fast` | `34` |
| `slow` | `55` |
| `signal_length` | `13` |

## Döndürdükleri

| Kolon |
| --- |
| `KVO_34_55` |
| `KVOs_34_55` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.klinger_volume_oscillator(df['high'], df['low'], df['close'], df['volume']).tail(3)
```

```text
               KVO_34_55    KVOs_34_55
date                                  
2024-10-25 -1.865480e+06 -1.177855e+06
2024-10-26 -1.784800e+06 -1.264561e+06
2024-10-27 -1.735052e+06 -1.331774e+06
```

**Accessor biçimi:** `df.zta.klinger_volume_oscillator(...)`

## Nasıl okunur

[macd](macd.md) gibi okunur: KVO ile kendi sinyal çizgisi arasındaki kesişim, ya da KVO'nun sıfırı kesmesi, bir fiyat hareketini arkasında gerçek hacim kararlılığıyla doğrular.

## Dikkat edilmesi gerekenler

Trend/cm muhasebesi, tek bir eksik barın düz bir EMA boşluğundan daha fazla etkiye sahip olduğu anlamına gelir — bir NaN bar, hemen sonrasındaki barın trend karşılaştırmasını da bozar, tam olarak ancak art arda iki temiz bar mevcut olduğunda toparlanır.

## Kaynak

Formül kaynağı: [https://tulipindicators.org/kvo](https://tulipindicators.org/kvo)
