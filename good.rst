====
Test
====

.. code-block:: c

    float foo(int n)
    {
        // Test C99.
        float x[n];
        x[0] = 1;
        return x[0];
    }

.. code-block:: cpp

    #include <iostream>

    int main()
    {
    }
    float foo(int n)
    {
        float x[n];
        x[0] = 1;
        return x[0];
    }

.. code-block:: python

    print(1)
