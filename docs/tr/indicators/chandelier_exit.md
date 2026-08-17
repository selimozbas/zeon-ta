# Chandelier Exit

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/chandelier_exit.md)

`zeonta.chandelier_exit()` — ATR-based trailing stop set from the recent n-bar high/low.

## Ne ölçer

`supertrend` ve `parabolic_sar`'ın kullandığı volatiliteye dayalı iz süren stop mantığını taşır, ama farklı kurulmuştur: bar bar ileri doğru zincirlenmek yerine, her seferinde son `n` bar'ın uç noktasından ve ATR'sinden yeniden hesaplanır. Bu, üzerinde düşünmeyi kolaylaştırır — takip edilecek bir iç durum yoktur — ama aynı zamanda, o iki göstergenin aksine, çizginin kendisinin bir bardan diğerine açık pozisyonun aleyhine hareket edebileceği anlamına da gelir.

## Formül

```text
Uzun = EnYüksekZirve(n) - ATR(n) x çarpan; Kısa = EnDüşükDip(n) + ATR(n) x çarpan
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `22` |
| `multiplier` | `3.0` |

## Döndürdükleri

| Kolon |
| --- |
| `CELONG_22_3.0` |
| `CESHORT_22_3.0` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.chandelier_exit(df['high'], df['low'], df['close']).tail(3)
```

```text
            CELONG_22_3.0  CESHORT_22_3.0
date                                     
2024-10-25      89.639229       92.259671
2024-10-26      89.634478       92.264422
2024-10-27      89.572493       91.472007
```

**Accessor biçimi:** `df.zta.chandelier_exit(...)`

## Nasıl okunur

Uzun bir pozisyonu `CELONG`'un üzerinde tutun; altına kapanış çıkış sinyalidir. Kısa bir pozisyonu `CESHORT`'un altında tutun; üzerine kapanış çıkış sinyalidir. Hangi çizginin geçerli olduğu tamamen elde tutulan pozisyona bağlıdır — göstergenin kendisinin hangi tarafta olduğunuz konusunda bir görüşü yoktur.

## Dikkat edilmesi gerekenler

Her bar stopu zincirlemek yerine sıfırdan yeniden hesapladığından, taze (daha düşük) bir zirve ile daha geniş bir ATR okuması bir araya geldiğinde, trend tamamen sağlam olsa bile uzun stopu *aşağı* çekebilir — bu gerçek bir geri çekilmedir, hata değil. Bazı grafik platformları düz formülün üzerine isteğe bağlı tek yönlü bir zincirleme ekler; bu uygulama yayınlanan formülü zincirleme olmadan, aynen izler.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit)
