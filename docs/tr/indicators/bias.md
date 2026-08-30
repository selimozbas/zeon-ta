# Sapma (Bias)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/bias.md)

`zeonta.bias()` — Percentage deviation of Close from its own SMA.

## Ne ölçer

Çin/Tayvan teknik analizinin bir temel taşı: fiyatın kendi hareketli ortalamasından ne kadar uzaklaştığına bir rakam koyar. [efficiency_ratio](efficiency_ratio.md) ya da [choppiness_index](choppiness_index.md) bir *pencerenin* nasıl hareket ettiğini tanımlarken, Bias tek bir mesafeyi tanımlar — fiyatın kendi ortalamasından şu anki farkı, başka bir şey değil.

## Formül

```text
BIAS = (Kapanış - SMA(Kapanış, length)) / SMA(Kapanış, length) * 100
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `26` |

## Döndürdükleri

| Kolon |
| --- |
| `BIAS_26` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.bias(df['close']).tail(3)
```

```text
date
2024-10-25   -0.861441
2024-10-26   -1.828151
2024-10-27   -2.366023
Name: BIAS_26, dtype: float64
```

**Accessor biçimi:** `df.zta.bias(...)`

## Nasıl okunur

Büyük bir pozitif ya da negatif okuma genellikle "aşırı gerilmiş" olarak okunur — Bias sıfırdan ne kadar uzaklaşırsa, ortalamaya doğru bir geri çekilme (pozitifse) ya da ondan uzaklaşan bir sıçrama (negatifse) o kadar olası hale gelir.

## Dikkat edilmesi gerekenler

Pencerenin SMA'sının tam olarak `0` olduğu her yerde, tanımsız bir bölme yerine `NaN` olur.

## Kaynak

Formül kaynağı: [https://research.titanfx.com/technical-analysis/ma/bias](https://research.titanfx.com/technical-analysis/ma/bias)
