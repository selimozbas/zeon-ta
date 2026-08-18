# Super Smoother Filtresi (Ehlers)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/super_smoother.md)

`zeonta.super_smoother()` — Ehlers' 2-pole low-pass filter: less lag than an EMA of the same critical period.

## Ne ölçer

İki kutuplu bir dijital alçak geçiren filtre; klasik finans literatüründen değil, Ehlers'in havacılık analog filtre tasarımı geçmişinden geliyor: sıradan bir hareketli ortalamanın doğrudan geçirdiği yüksek frekanslı titremeyi kaldırır, aynı kritik periyottaki bir EMA'dan anlamlı ölçüde daha az gecikmeyle. `t3` gecikmeyi DEMA-tarzı düzeltmeleri zincirleyerek azaltırken, bu tamamen farklı bir yoldan azaltır — gerçek bir dijital sinyal işleme filtre tasarımı.

## Formül

```text
a1 = exp(-1,414 x pi / n); b1 = 2 x a1 x cos(1,414 x pi / n); c2 = b1; c3 = -a1^2; c1 = 1 - c2 - c3; SSF = c1 x (Kapanış + Kapanış[t-1]) / 2 + c2 x SSF[t-1] + c3 x SSF[t-2]
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `SSF_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.super_smoother(df['close']).tail(3)
```

```text
date
2024-10-25    90.403862
2024-10-26    90.276889
2024-10-27    90.078809
Name: SSF_20, dtype: float64
```

**Accessor biçimi:** `df.zta.super_smoother(...)`

## Nasıl okunur

Diğer herhangi bir hareketli ortalama gibi okuyun — trend yönü, dinamik destek ve direnç, bir kesişim sistemi için taban çizgisi — ama fiyata belirgin biçimde daha sıkı yapışmasını, dalgalı veride aynı uzunluktaki düz bir `sma`/`ema`'nın göstereceği çalkantılı titremenin daha azını bekleyin.

## Dikkat edilmesi gerekenler

``cos()``'un argümanı radyan cinsinden olmalıdır; popüler açık kaynaklı bir referans uygulama, Ehlers'in orijinal EasyLanguage sabitini (derece tabanlı bir ``Cos()`` için tasarlanmış ``180``) radyan tabanlı bir dile taşırken dönüştürmeden bırakmış — bu sessizce farklı (yanlış) bir filtre üretir; bu, o uygulamanın kaynak kodu doğrudan incelenerek doğrulanmıştır. Bu uygulama baştan sona radyan-tutarlı biçimi kullanır.

## Kaynak

Formül kaynağı: [https://www.mesasoftware.com/papers/EhlersSuperSmoother.pdf](https://www.mesasoftware.com/papers/EhlersSuperSmoother.pdf)
