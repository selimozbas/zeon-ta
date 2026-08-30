# Psikolojik Çizgi (PSL)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/psl.md)

`zeonta.psl()` — Percentage of up-closes over a rolling window — raw market sentiment.

## Ne ölçer

Saf bir oy-sayma duyarlılık göstergesi: yuvarlanan bir pencerede fiyatın önceki kapanışın üzerinde kapandığı barların oranı, yüzde olarak. Bu kütüphanedeki oran-tabanlı her osilatörden ([rsi](rsi.md), [cmo](cmo.md), ...) farklı olarak, PSL yalnızca fiyatın *ne sıklıkla* yükseldiğini sorar, *ne kadar* yükseldiğini hiç sormaz.

## Formül

```text
PSL = (son n bar içindeki yükseliş-kapanışlı bar sayısı) / n * 100
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `12` |

## Döndürdükleri

| Kolon |
| --- |
| `PSL_12` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.psl(df['close']).tail(3)
```

```text
date
2024-10-25    33.333333
2024-10-26    33.333333
2024-10-27    25.000000
Name: PSL_12, dtype: float64
```

**Accessor biçimi:** `df.zta.psl(...)`

## Nasıl okunur

50'nin üstü, pencerenin barlarının yarısından fazlasının yükselişle kapandığı anlamına gelir; 50'nin altı tam tersidir. Kabaca 75'in üstü ya da 25'in altındaki okumalar genellikle aşırı-alım/aşırı-satım duyarlılık uçları olarak okunur.

## Dikkat edilmesi gerekenler

Değişmeyen bir kapanış (önceki bardan farksız), çoğu yükseliş/düşüş-günü sayacıyla aynı kuralla yükseliş *sayılmaz*.

## Kaynak

Formül kaynağı: [https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/indicator/psychological_line_indicator_.htm](https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/indicator/psychological_line_indicator_.htm)
