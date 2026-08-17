# Vortex İndikatörü

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/vortex.md)

`zeonta.vortex()` — Compares how far price moved from the prior bar's opposite extreme, both directions.

## Ne ölçer

Her çizgi, geçerli barın aralığının önceki barın *karşıt* ucundan ne kadar uzaklaştığını ölçer, bir pencere boyunca toplanır ve aynı pencerenin gerçek aralığına göre normalize edilir. +VI bir yükseliş trendinde -VI'nin önünde gider ve ikisi trend değişimleri civarında kesişir — `adx`'in +DI/-DI çizgilerinin sahip olduğu aynı yönsel çift ilişkisi, ama Vortex baştan sona Wilder yumuşatması yerine düz kayan toplamlar kullanır; bu yüzden daha hızlı tepki verir ve pencereden çıkan eski barları tamamen unutur.

## Formül

```text
+VM = |Yüksek - ÖncekiDüşük|; -VM = |Düşük - ÖncekiYüksek|; +VI = Toplam(+VM, n) / Toplam(GerçekAralık, n); -VI = Toplam(-VM, n) / Toplam(GerçekAralık, n)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `VTXP_14` |
| `VTXM_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vortex(df['high'], df['low'], df['close']).tail(3)
```

```text
             VTXP_14   VTXM_14
date                          
2024-10-25  1.002726  1.050817
2024-10-26  0.913460  1.066400
2024-10-27  0.872397  1.093248
```

**Accessor biçimi:** `df.zta.vortex(...)`

## Nasıl okunur

+VI'nin -VI'nin üzerine çıkması boğa sinyali, tersi ayı sinyali olarak okunur — iki çizgi ne kadar birbirinden uzaklaşırsa, ima edilen trend o kadar güçlüdür. Çizgiler düz toplamlar kullandığından, yönsel harekette taze bir patlamaya hızlı tepki verirler; bu da gerçekten dalgalı bir piyasada, ADX'in DI çizgileri gibi Wilder-yumuşatılmış bir çiftin vereceğinden daha fazla kesişim (ve daha fazla yanlış sinyal) anlamına gelir.

## Dikkat edilmesi gerekenler

Vortex'in RSI veya Stokastik gibi sabit bir üst sınırı yoktur — her iki çizgi de genellikle 0.5 ila 1.5 civarında oturur, ama yeterince keskin bir hareket ikisinden birini daha da yükseğe itebilir; bu yüzden mutlak seviyeye temkinli yaklaşın ve bunun yerine kesişime ve iki çizgi arasındaki farka dayanın.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/vortex-indicator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/vortex-indicator)
