# Complex data

This playground is about using complex data structures like knowledge graphs, onthologies and teaching models how to leverage and generate complex data structures.

![graphs](/img/graphs.png)

## Knowledge graphs

Use a model to create a knowledge graph to answer a question

```
python knowledge-graphs.py
```

Take a look at the generated svg image


## Using Onthologies for structured domain knowledge

Use a vision model to create an onthology in OWL format based on pictures

```
python create_onthologies.py 
```

Check out `screws.xml`

Give a model access to an onthology to structure its response in the knowledge of a domain

```
python use-onthology.py

```

Take a look at the output 


## Processing documents for specific values

Take a look at the invoice example [sample invoic](https://likvi.de/assets/img/blog/rechnungsvorlage.jpg), the [expected invoice xml](invoice_template.xml) schema and some [explaination about the expected xml format](invoice_explaination.txt).

```
python parse_invoice.py 
```

Check out `invoice_parsed.xml` to see which kind of details the model was able to extract