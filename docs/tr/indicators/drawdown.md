# Düşüş (Drawdown)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/drawdown.md)

`zeonta.drawdown()` — Percentage decline from the running peak, since the start of the series.

## Ne ölçer

Serinin şimdiye kadarki kendi tüm-zamanlar zirvesinden süregelen yüzde düşüş — [cumulative_return](cumulative_return.md)'un toplam kazanca uyguladığı aynı fikir, burada zirveden kayıp için uygulanır.

## Formül

```text
DD = (Kapanış - KümülatifMaks(Kapanış)) / KümülatifMaks(Kapanış) * 100
```

## Parametreler

**Gerekli girdiler:** `close`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `DD` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.drawdown(df['close']).tail(3)
```

```text
date
2024-10-25   -13.421818
2024-10-26   -14.360861
2024-10-27   -14.972795
Name: DD, dtype: float64
```

**Accessor biçimi:** `df.zta.drawdown(...)`

## Nasıl okunur

Her zaman `<= 0`; her yeni zirvede tam olarak `0` olur. Bir geçmiş boyunca ulaşılan en negatif değer, onun maksimum düşüşüdür — ne zaman olduğundan bağımsız olarak en kötü dönemin ne kadar kötü olduğunu tanımlamanın standart yolu.

## Dikkat edilmesi gerekenler

`cumulative_return` gibi, bu da sabit bir uzunluk yerine verdiğiniz serinin başına kadar geriye bakar — daha fazla geçmiş eklemek yalnızca süregelen zirveyi yükseltebilir, bu da her sonraki değeri değiştirebilir.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Drawdown_(economics)](https://en.wikipedia.org/wiki/Drawdown_(economics))
