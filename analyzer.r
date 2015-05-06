# libraries
# library(ggplot2)
# library(plyr)
# library(reshape2)

# copy the following so you can do sme()
WORKDIRECTORY='/work/directory'
THISFILE     ='thisfile.r'
setwd(WORKDIRECTORY)
sme <- function()
{
    setwd(WORKDIRECTORY)
    source(THISFILE)
}

explore.HBO <- function()
{
    transfer <- function()
    {
    }
    load <- function()
    {
        datatext = """
        order               time
        h()=random()        18.921395
        h()=offset          8.161882
        h()=-offset         74.934069
        """
    }

    clean <- function(d)
    {
    }

    func <- function(d)
    {
    }

    do_main <- function()
    {
        d = load()
        d = clean(d)
        func(d)
    }
    do_main()
}

main <- function()
{
    explore.FSJ386323()
}
main()
