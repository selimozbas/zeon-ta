# Normalize Edilmiş Ortalama Gerçek Aralık (NATR)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/natr.md)

`zeonta.natr()` — ATR expressed as a percentage of price, so different symbols become comparable.

## Ne ölçer

[atr](atr.md) ham bir fiyat miktarı bildirir — 2 dolarlık bir ATR, 10 dolarlık bir hisse için devasa, 2.000 dolarlık bir hisse için ise önemsizdir. NATR aynı ölçümü bunun yerine fiyatın yüzdesi olarak ifade eder, böylece farklı semboller (ya da zaman içinde çok farklı fiyat seviyelerindeki aynı sembol) doğrudan karşılaştırılabilir hale gelir.

## Formül

```text
NATR = ATR(n) / Kapanış * 100
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `NATR_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.natr(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    1.330037
2024-10-26    1.340412
2024-10-27    1.380133
Name: NATR_14, dtype: float64
```

**Accessor biçimi:** `df.zta.natr(...)`

## Nasıl okunur

ATR ile aynı şekilde okunur — yükselmesi oynaklığın arttığı anlamına gelir — ama *seviyesini* semboller arasında ya da uzun bir fiyat geçmişi boyunca, ham ATR ile asla yapamayacağınız şekilde karşılaştırabilirsiniz.

## Dikkat edilmesi gerekenler

`Kapanış` tam olarak `0` olduğunda, tanımsız bir bölüm yerine `NaN` olur.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000501823-average-true-range-natr/](https://www.tradingview.com/support/solutions/43000501823-average-true-range-natr/)
