Overview
========

Click on a nut name for more details.


**Decorators & Wrappers** : convert plain Python functions to nuts

.. code:: Python

  GreaterThan2 = nut_filter(lambda x: x > 2)
  [1, 2, 3, 4] >> GreaterThan2() >> Collect()   --> [3, 4]

- :func:`nut_filter <nutsflow.factory.nut_filter>` :
  wrapper to create nut filters.

- :func:`nut_filterfalse <nutsflow.factory.nut_filterfalse>` :
  wrapper to create nut filters with inversed logic.

- :func:`nut_function <nutsflow.factory.nut_function>` :
  wrapper for nut functions that operate on elements.

- :func:`nut_processor <nutsflow.factory.nut_processor>` :
  wrapper for nut processors that operate on iterables.  

- :func:`nut_sink <nutsflow.factory.nut_sink>` :
  wrapper for nut sinks that aggregate data flows.  

- :func:`nut_source <nutsflow.factory.nut_source>` :
  wrapper for nut sources that generate data.     



**Sources** : generate iterable data

.. code:: Python

  Range(5) >> Collect()   --> [0, 1, 2, 3, 4]

- :class:`Empty <nutsflow.source.Empty>` :
  empty source that does not generate anything.

- :class:`Enumerate <nutsflow.source.Enumerate>` :
  generate infinite number of increasing integers.

- :class:`Product <nutsflow.source.Product>` :
  generate Cartesian product of iterables.

- :class:`Range <nutsflow.source.Range>` :
  generate range of integer numbers.

- :class:`ReadCSV <nutsflow.source.ReadCSV>` :
  read elements from file in CSV (or TSV) format.

- :class:`Repeat <nutsflow.source.Repeat>` :
  repeats a value n times or infinitely.


**Sinks** : aggregate iterable data

.. code:: Python

  [1, 2, 3] >> Count()   --> 3

- :class:`ArgMax <nutsflow.sink.ArgMax>` :
  return index of largest element.

- :class:`ArgMin <nutsflow.sink.ArgMin>` :
  return index of smallest element.

- :class:`Collect <nutsflow.sink.Collect>` :
  collect elements in a container, e.g. list, set, dict.

- :class:`Consume <nutsflow.sink.Consume>` :
  consumes input and returns nothing.

- :class:`Count <nutsflow.sink.Count>` :
  count number of elements.

- :class:`CountValues <nutsflow.sink.CountValues>` :
  return dictionary with counts of the different values.

- :class:`Head <nutsflow.sink.Head>` :
  collect first n elements in a container, e.g. list, set, dict.

- :class:`Join <nutsflow.sink.Join>` :
  join elements in a string.

- :class:`Max <nutsflow.sink.Max>` :
  return largest element.

- :class:`Mean <nutsflow.sink.Mean>` :
  compute mean value of elements.

- :class:`MeanStd <nutsflow.sink.MeanStd>` :
  compute mean and standard deviation.

- :class:`Min <nutsflow.sink.Min>` :
  return smallest element.

- :class:`Next <nutsflow.sink.Next>` :
  get next element.

- :class:`Nth <nutsflow.sink.Nth>` :
  get n-th element.

- :class:`Reduce <nutsflow.sink.Reduce>` :
  reduce inputs with a given function.

- :class:`Sum <nutsflow.sink.Sum>` :
  return sum of elements.

- :class:`Tail <nutsflow.sink.Tail>` :
  collect last n elements in a container, e.g. list, set, dict.

- :class:`Unzip <nutsflow.sink.Unzip>` :
  reverses Zip() and unzips tuple elements.
 
- :class:`WriteCSV <nutsflow.sink.WriteCSV>` :
  write elements to file in CSV (or TSV) format.

  
**Functions** : operate on individual elements and return elements

.. code:: Python

  [1, 2, 3] >> Square() >> Collect()   --> [1, 4, 9]

- :class:`Counter <nutsflow.function.Counter>` :
  counts elements in an external variable - use for debugging only.

- :class:`Format <nutsflow.function.Format>` :
  format element as a string.  

- :class:`Get <nutsflow.function.Get>` :
  extract slice from (indexable) element. 

- :class:`GetCols <nutsflow.function.GetCols>` :
  extract columns from (indexable) element.

- :class:`Identity <nutsflow.function.Identity>` :
  returns the unchanged element. 

- :class:`NOP <nutsflow.function.NOP>` :
  no operation. disable individual nuts temporarily - use for debugging only. 

- :class:`Print <nutsflow.function.Print>` :
  print element to console. 

- :class:`Sleep <nutsflow.function.Sleep>` :
  pause processing thread for a given time. 

- :class:`Square <nutsflow.function.Square>` :
  return square of element. 


**Processors** : operate on iterables and return iterables

.. code:: Python

  [1, 2, 3, 4] >> Take(2) >> Collect()   --> [1, 2]

- :class:`Append <nutsflow.processor.Append>` :
  append to the elements of the iterable.  
  
- :class:`Cache <nutsflow.processor.Cache>` :
  caches elements on disk.

- :class:`Chunk <nutsflow.processor.Chunk>` :
  split iterable in chunks of size n.
  
- :class:`ChunkWhen <nutsflow.processor.ChunkWhen>` :
  create new chunk whenever predicate function is true.

- :class:`ChunkBy <nutsflow.processor.ChunkBy>` :
  create new chunk whenever function value changes.
  
- :class:`Clone <nutsflow.processor.Clone>` :
  clone elements in iterables n times.  

- :class:`Combine <nutsflow.processor.Combine>` :
  combines elements in subsequences of length r.

- :class:`Concat <nutsflow.processor.Concat>` :
  concatenates iterables.

- :class:`Cycle <nutsflow.processor.Cycle>` :
  cycle through elments of input iterable infinitely.

- :class:`Dedupe <nutsflow.processor.Dedupe>` :
  removes duplicates from iterable.

- :class:`Drop <nutsflow.processor.Drop>` :
  drops first n elements.

- :class:`DropWhile <nutsflow.processor.DropWhile>` :
  drops first elements while predicate function is true.

- :class:`Filter <nutsflow.processor.Filter>` :
  drops elements predicate function is false.

- :class:`FilterFalse <nutsflow.processor.FilterFalse>` :
  drops elements predicate function is true.

- :class:`FlatMap <nutsflow.processor.FlatMap>` :
  maps function on elements and flattens result.

- :class:`Flatten <nutsflow.processor.Flatten>` :
  flattens iterables within the input iterable.

- :class:`FlattenCol <nutsflow.processor.FlattenCol>` :
  extract given columns from (indexable) elements and flattens result.

- :class:`GroupBy <nutsflow.processor.GroupBy>` :
  groups elements based on grouping function.

- :class:`GroupBySorted <nutsflow.processor.GroupBySorted>` :
  groups presorted iterable of elements.

- :class:`If <nutsflow.processor.If>` :
  executes nut depending on condition.

- :class:`Insert <nutsflow.processor.Insert>` :
  insert into the elements of the iterable.  
  
- :class:`Interleave <nutsflow.processor.Interleave>` :
  interleaves elements of multiple iterables.

- :class:`Map <nutsflow.processor.Map>` :
  maps function on elements.

- :class:`MapCol <nutsflow.processor.MapCol>` :
  maps function on specific columns of (indexable) elements.

- :class:`MapMulti <nutsflow.processor.MapMulti>` :
  maps multiple functions on elements, resulting in multiple output iterators.

- :class:`MapPar <nutsflow.processor.MapPar>` :
  map function (in concurrent threads) on elements.

- :class:`Partition <nutsflow.processor.Partition>` :
  split iterable into two partitions based on predicate function.

- :class:`Permutate <nutsflow.processor.Permutate>` :
  return successive r length permutations of elements.

- :class:`Pick <nutsflow.processor.Pick>` :
  pick every n-th element or sample with given probability from iterable.

- :class:`Prefetch <nutsflow.processor.Prefetch>` :
  pre-fetch elements in separate thread.

- :class:`PrintProgress <nutsflow.processor.PrintProgress>` :
  print progress on iterable.

- :class:`Shuffle <nutsflow.processor.Shuffle>` :
  shuffle elements (partially).

- :class:`Slice <nutsflow.processor.Slice>` :
  return slice of iterable.

- :class:`Take <nutsflow.processor.Take>` :
  return first n elements.

- :class:`TakeWhile <nutsflow.processor.TakeWhile>` :
  return elements while predicate function is true.

- :class:`Tee <nutsflow.processor.Tee>` :
  return n independent iterators over iterable.

- :class:`Try <nutsflow.processor.Try>` :
  handle exceptions.

- :class:`Window <nutsflow.processor.Window>` :
  return sliding window over elements of iterable.
  
- :class:`Zip <nutsflow.processor.Zip>` :
  zip elements from multiple iterables.

- :class:`ZipWith <nutsflow.processor.ZipWith>` :
  zips elements from multiple iterables with a given function.
