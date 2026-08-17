# Keltner Kanalları

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/keltner.md)

`zeonta.keltner()` — EMA envelope scaled by ATR — smoother and less reactive than Bollinger.

## Ne ölçer

Bollinger Bantları ile aynı fikir, tek bir değişiklikle: standart sapma yerine ATR. ATR standart sapmadan daha yavaş tepki verdiği için, Keltner Kanalları bir şok boyunca daha yumuşak kalır — ikisini birlikte kullanmayı yararlı kılan da tam olarak budur.

## Formül

```text
Orta Çizgi = EMA(Kapanış, 20); Üst Bant = Orta + 2 x ATR(10); Alt Bant = Orta - 2 x ATR(10)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |
| `atr_length` | `10` |
| `multiplier` | `2.0` |

## Döndürdükleri

| Kolon |
| --- |
| `KCL_20_2.0` |
| `KCM_20_2.0` |
| `KCU_20_2.0` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.keltner(df['high'], df['low'], df['close']).tail(3)
```

```text
            KCL_20_2.0  KCM_20_2.0  KCU_20_2.0
date                                          
2024-10-25   88.199025   90.721181   93.243337
2024-10-26   88.069492   90.568592   93.067693
2024-10-27   87.807278   90.369888   92.932498
```

**Accessor biçimi:** `df.zta.keltner(...)`

## Nasıl okunur

Kanalın dışında bir kapanış gerçek bir kırılım adayıdır, çünkü kanal bir Bollinger bandına kıyasla çok daha isteksiz genişler. İki kanalı karşılaştırmak [squeeze](squeeze.md) göstergesinin temelidir.

## Dikkat edilmesi gerekenler

Uygulamalar beklediğinizden çok daha fazla farklılık gösterir: bazıları orta çizgi için EMA yerine SMA kullanır, eski sürümler ise ATR yerine basit yüksek-düşük aralığını kullanır. Bu çıktıyı bir grafikle karşılaştırmadan önce tanımı kontrol edin.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/keltner-channels](https://ta.cognicode.org/learn/keltner-channels)
