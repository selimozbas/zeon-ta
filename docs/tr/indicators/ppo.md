# Yüzde Fiyat Osilatörü (PPO)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ppo.md)

`zeonta.ppo()` — MACD expressed as a percentage, comparable across symbols and price levels.

## Ne ölçer

Tam olarak `macd`'nin kurulumu, mutlak fiyat farkını yüzdeye çevirmek için yavaş EMA'ya bölünmüş hâli. PPO okuması 5 ise, menkul kıymet 5 dolardan da 500 dolardan da işlem görse hızlı EMA yavaş olanın %5 üzerindedir — `macd`'nin kendi ham çıktısının semboller arasında yapamayacağı bir karşılaştırma.

## Formül

```text
PPO = (EMA(Kapanış, hızlı) - EMA(Kapanış, yavaş)) / EMA(Kapanış, yavaş) x 100; Sinyal = EMA(PPO, sinyal); Histogram = PPO - Sinyal
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `fast` | `12` |
| `slow` | `26` |
| `signal` | `9` |

## Döndürdükleri

| Kolon |
| --- |
| `PPO_12_26_9` |
| `PPOs_12_26_9` |
| `PPOh_12_26_9` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ppo(df['close']).tail(3)
```

```text
            PPO_12_26_9  PPOs_12_26_9  PPOh_12_26_9
date                                               
2024-10-25    -0.419527     -0.376846     -0.042681
2024-10-26    -0.509810     -0.403439     -0.106371
2024-10-27    -0.631409     -0.449033     -0.182376
```

**Accessor biçimi:** `df.zta.ppo(...)`

## Nasıl okunur

Tam olarak `macd` gibi okuyun: sinyal çizgisi kesişimleri, orta çizgi kesişimleri ve uyumsuzluklar aynı anlamı taşır, sadece farklı semboller arasında tarama yaparken karşılaştırılabilir kalan bir yüzde ölçeğinde.

## Dikkat edilmesi gerekenler

Yavaş EMA'ya böldüğü için, fiyatı (ve dolayısıyla EMA'sı) sıfırdan geçen bir menkul kıymette PPO kısa süreliğine tanımsız ya da aşırı ölçeklenmiş olur — bu yalnızca negatif olabilen spread/sentetik seriler için önemlidir, sıradan fiyatlar için değil.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo)
