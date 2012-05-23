import train
import test
import time

if __name__=='__main__':
    import load_config
    t_start = time.time()
    params_filename = train.run(load_config.cfg)
    test.run(load_config.cfg, params_filename)
    print 'run completed in %s sec' % (time.time() - t_start)
