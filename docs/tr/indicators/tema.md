# Üçlü Üssel Hareketli Ortalama (TEMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/tema.md)

`zeonta.tema()` — EMA with even less lag than DEMA, by combining three nested EMAs.

## Ne ölçer

`dema` ile aynı gecikme-iptal fikri, bir yumuşatma adımı daha ileri taşınmış hâli. Düz bir fiyat hareketi DEMA altında zaten neredeyse mükemmel iptal olurken, TEMA'nın ek terimi bu iptali *eğrisel* hareketlerde de — hızlanma ve yavaşlamalarda — sürdürür; tam da DEMA'nın kendisinin yeniden geride kalmaya başladığı yerlerde.

## Formül

```text
TEMA = (3 x EMA1) - (3 x EMA2) + EMA3, burada EMA1 = EMA(Kapanış, n), EMA2 = EMA(EMA1, n) ve EMA3 = EMA(EMA2, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `TEMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.tema(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.151836
2024-10-26    89.833830
2024-10-27    89.413759
Name: TEMA_20, dtype: float64
```

**Accessor biçimi:** `df.zta.tema(...)`

## Nasıl okunur

`dema` ya da `ema` gibi okuyun, ama tam olarak DEMA'nın kaymaya başladığı yerde ona en çok güvenin: düz bir çizgide hareket etmekle kalmayıp kendisi hızlanan ya da yavaşlayan bir trend.

## Dikkat edilmesi gerekenler

Üç katmanlı gecikme iptali, üç katmanlı aşırı tepki riski demektir — TEMA, gürültüye `dema`'dan bile daha isteklice tepki verir ve düz bir EMA'nın kabaca üç katı ısınma süresine ihtiyaç duyar (`EMA3`, zaten ısınmış tam bir `EMA2` penceresi gerektirir).

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/triple-exponential-moving-average-tema](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/triple-exponential-moving-average-tema)
