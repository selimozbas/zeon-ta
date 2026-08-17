# Birikim/Dağıtım Çizgisi (ADL)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/adl.md)

`zeonta.adl()` — Running total of volume weighted by where the close sits in its own range.

## Ne ölçer

`obv` yalnızca kapanışın yukarı mı aşağı mı olduğunu sorup barın *tüm* hacmini bir tarafa yazarken, ADL kapanışın *barın tüm aralığının neresine* düştüğünü sorar ve hacmi bu kademeli konuma göre ağırlıklandırır — zirveye yakın ama tam onda olmayan bir kapanış, hacminin tamamını değil çoğunu pozitif katkı olarak sayar. Aynı zamanda `cmf`'nin kümülatif toplam hâlidir; `cmf` bunun yerine aynı bar-başına akışı sabit bir pencerede toplayıp hacme bölerek sınırlı bir oran elde eder.

## Formül

```text
PAÇ = ((Kapanış - Düşük) - (Yüksek - Kapanış)) / (Yüksek - Düşük); PAH = PAÇ x Hacim; ADL = Önceki ADL + PAH
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`, `volume`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `ADL` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.adl(df['high'], df['low'], df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    1.563072e+06
2024-10-26    1.207817e+06
2024-10-27    1.082389e+06
Name: ADL, dtype: float64
```

**Accessor biçimi:** `df.zta.adl(...)`

## Nasıl okunur

Tam olarak `obv` gibi okuyun: mutlak seviye keyfidir (serinin nereden başladığına bağlıdır), yalnızca *eğimi* ve fiyatla uyuşup uyuşmadığı önemlidir. Fiyat yatay ya da düşerken ADL'nin yükselmesi, yüzeyin altında birikim oluştuğu şeklinde okunur — `obv`'nin kullanıldığı aynı boğa-uyumsuzluğu fikri, sadece daha kademeli bir girdiyle.

## Dikkat edilmesi gerekenler

Çok dar bir yüksek-düşük aralığı, Para Akışı Çarpanı'nın paydasını küçültür; bu yüzden sakin bir bardaki sıradan hacim, aslında pek bir şey olmamasına rağmen ADL'yi sert sallayabilir — bu uygulama tam sıfır-aralık durumunu patlamak yerine hiçbir katkı yapmayacak şekilde tanımlar, ama sıfıra yakın aralıklar yine de gürültülüdür. `obv` gibi, doğal bir sıfırlama noktası olmayan bir kümülatif toplamdır; bu yüzden iki farklı zaman penceresindeki mutlak seviyeleri karşılaştırmak size hiçbir şey söylemez.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line)
