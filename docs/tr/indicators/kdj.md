# KDJ

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/kdj.md)

`zeonta.kdj()` — Stochastic %K/%D reworked with Wilder smoothing, plus a fast, overshooting J line.

## Ne ölçer

Çin piyasası teknik analizinde popüler bir stokastik varyantı. [stoch](stoch.md)'un yumuşatmadan önce `%K` dediği aynı Ham Stokastik Değer'den başlar, sonra düz bir SMA yerine onu Wilder'ın özyinelemesiyle ([smma](smma.md)'nın sunduğu aynı yöntem) iki kez yumuşatır. `J`, `K`/`D` hareketini ortalamak yerine onun ötesine ekstrapolasyon yapar, bu yüzden olağan 0-100 aralığının dışına taşar — amacı, `K` ve `D` kendi uçlarına ulaşmadan *önce* aşırı-alım/aşırı-satım koşullarını işaret etmektir.

## Formül

```text
RSV = 100*(Kapanış-DD)/(YY-DD); K = Wilder(RSV, signal); D = Wilder(K, signal); J = 3*K - 2*D
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `9` |
| `signal` | `3` |

## Döndürdükleri

| Kolon |
| --- |
| `K_9_3` |
| `D_9_3` |
| `J_9_3` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kdj(df['high'], df['low'], df['close']).tail(3)
```

```text
                K_9_3      D_9_3      J_9_3
date                                       
2024-10-25  32.635164  33.577094  30.751304
2024-10-26  23.761553  30.305247  10.674166
2024-10-27  19.677575  26.762690   5.507346
```

**Accessor biçimi:** `df.zta.kdj(...)`

## Nasıl okunur

`stoch` gibi okunur: `K` ve `D` arasındaki kesişimler momentum kaymalarını işaret eder, `J` ikisine de öncülük eder — 100'ün oldukça üstünde ya da 0'ın altında bir `J` okuması, bir uç noktanın en erken uyarısıdır.

## Dikkat edilmesi gerekenler

`J`, tasarım gereği sınırsızdır — `K`/`D`'nin doğal olarak olduğu gibi onu 0-100'e sıkıştırmayın.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/scripts/kdj/](https://www.tradingview.com/scripts/kdj/)
