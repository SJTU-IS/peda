
import re

E = re.compile(r'^([^ /=]+),$')

class JSCAnalyzer:
    def __init__(self, fpath):
        with open(fpath, 'r') as f:
            self.lines_ = f.readlines()

    def process_js_type_list(self):
        define_enum = 'enum JSType : uint8_t {'
        stage = 0
        names = []
        for line in self.lines_:
            line = line.strip()
            if not line:
                continue
            if stage == 2:
                return names
            if stage == 0:
                if define_enum in line:
                    stage += 1
            else:
                if line.endswith('};'):
                    stage += 1
                result = E.match(line)
                if result:
                    name = result.group(1)
                    names.append(name)
    
    def process(self):
        return {k: v for (k, v) in enumerate(self.process_js_type_list())}

V = re.compile(r'V\((.+)\)')

class V8Analyzer:
    def __init__(self, fpath):
        with open(fpath, 'r') as f:
            self.lines_ = f.readlines()

    def process_instance_type_list(self):
        define_macro = '#define INSTANCE_TYPE_LIST'
        stage = 0
        names = []
        for line in self.lines_:
            line = line.strip()
            if not line:
                continue
            if stage == 2:
                return names
            if stage == 0:
                if define_macro in line:
                    stage += 1
            else:
                if not line.endswith('\\'):
                    stage += 1
                if 'ARRAY_ITERATOR_TYPE_LIST' in line:
                    names += self.process_array_iterator_type_list()
                    continue
                result = V.match(line)
                if result:
                    name = result.group(1)
                    names.append(name)

    def process_array_iterator_type_list(self):
        define_macro = '#define ARRAY_ITERATOR_TYPE_LIST'
        stage = 0
        names = []
        for line in self.lines_:
            line = line.strip()
            if not line:
                continue
            if stage == 2:
                return names
            if stage == 0:
                if define_macro in line:
                    stage += 1
            else:
                if not line.endswith('\\'):
                    stage += 1
                result = V.match(line)
                if result:
                    name = result.group(1)
                    names.append(name)

    def process(self):
        map_ = {}
        for (k, v) in self.process_string_type_list().items():
            map_[v] = k

        full_type_list = self.process_instance_type_list()
        symbol_index = full_type_list.index('SYMBOL_TYPE')
        for (i, v) in enumerate(full_type_list[symbol_index:]):
            map_[0x80+i] = v
            
        return map_
        
    def process_string_type_list(self):
        kIsNotStringMask = 0x80
        kStringTag = 0x0
        kNotStringTag = 0x80

        kIsNotInternalizedMask = 0x40
        kNotInternalizedTag = 0x40
        kInternalizedTag = 0x0

        kStringEncodingMask = 0x8
        kTwoByteStringTag = 0x0
        kOneByteStringTag = 0x8

        kStringRepresentationMask = 0x07

        kSeqStringTag = 0x0
        kConsStringTag = 0x1
        kExternalStringTag = 0x2
        kSlicedStringTag = 0x3
        kThinStringTag = 0x5

        kIsIndirectStringMask = 0x1
        kIsIndirectStringTag = 0x1

        kOneByteDataHintMask = 0x10
        kOneByteDataHintTag = 0x10

        kShortExternalStringMask = 0x20
        kShortExternalStringTag = 0x20

        kShortcutTypeMask = kIsNotStringMask | kIsNotInternalizedMask | kStringRepresentationMask
        kShortcutTypeTag = kConsStringTag | kNotInternalizedTag

        INTERNALIZED_STRING_TYPE = kTwoByteStringTag | kSeqStringTag |\
                                   kInternalizedTag
        ONE_BYTE_INTERNALIZED_STRING_TYPE =\
            kOneByteStringTag | kSeqStringTag | kInternalizedTag
        EXTERNAL_INTERNALIZED_STRING_TYPE =\
            kTwoByteStringTag | kExternalStringTag | kInternalizedTag
        EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE =\
            kOneByteStringTag | kExternalStringTag | kInternalizedTag
        EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE =\
            EXTERNAL_INTERNALIZED_STRING_TYPE | kOneByteDataHintTag |\
            kInternalizedTag
        SHORT_EXTERNAL_INTERNALIZED_STRING_TYPE = EXTERNAL_INTERNALIZED_STRING_TYPE |\
                                                  kShortExternalStringTag |\
                                                  kInternalizedTag
        SHORT_EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE =\
            EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE | kShortExternalStringTag |\
            kInternalizedTag
        SHORT_EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE =\
            EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE |\
            kShortExternalStringTag | kInternalizedTag
        STRING_TYPE = INTERNALIZED_STRING_TYPE | kNotInternalizedTag
        ONE_BYTE_STRING_TYPE =\
            ONE_BYTE_INTERNALIZED_STRING_TYPE | kNotInternalizedTag
        CONS_STRING_TYPE = kTwoByteStringTag | kConsStringTag | kNotInternalizedTag
        CONS_ONE_BYTE_STRING_TYPE =\
            kOneByteStringTag | kConsStringTag | kNotInternalizedTag
        SLICED_STRING_TYPE =\
            kTwoByteStringTag | kSlicedStringTag | kNotInternalizedTag
        SLICED_ONE_BYTE_STRING_TYPE =\
            kOneByteStringTag | kSlicedStringTag | kNotInternalizedTag
        EXTERNAL_STRING_TYPE =\
            EXTERNAL_INTERNALIZED_STRING_TYPE | kNotInternalizedTag
        EXTERNAL_ONE_BYTE_STRING_TYPE =\
            EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE | kNotInternalizedTag
        EXTERNAL_STRING_WITH_ONE_BYTE_DATA_TYPE =\
            EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE |\
            kNotInternalizedTag
        SHORT_EXTERNAL_STRING_TYPE =\
            SHORT_EXTERNAL_INTERNALIZED_STRING_TYPE | kNotInternalizedTag
        SHORT_EXTERNAL_ONE_BYTE_STRING_TYPE =\
            SHORT_EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE | kNotInternalizedTag
        SHORT_EXTERNAL_STRING_WITH_ONE_BYTE_DATA_TYPE =\
            SHORT_EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE |\
            kNotInternalizedTag
        THIN_STRING_TYPE = kTwoByteStringTag | kThinStringTag | kNotInternalizedTag
        THIN_ONE_BYTE_STRING_TYPE =\
            kOneByteStringTag | kThinStringTag | kNotInternalizedTag

        return {
            'INTERNALIZED_STRING_TYPE': kTwoByteStringTag | kSeqStringTag |\
                                    kInternalizedTag,
            'ONE_BYTE_INTERNALIZED_STRING_TYPE':\
                kOneByteStringTag | kSeqStringTag | kInternalizedTag,
            'EXTERNAL_INTERNALIZED_STRING_TYPE':\
                kTwoByteStringTag | kExternalStringTag | kInternalizedTag,
            'EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE':\
                kOneByteStringTag | kExternalStringTag | kInternalizedTag,
            'EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE':\
                EXTERNAL_INTERNALIZED_STRING_TYPE | kOneByteDataHintTag |\
                kInternalizedTag,
            'SHORT_EXTERNAL_INTERNALIZED_STRING_TYPE': EXTERNAL_INTERNALIZED_STRING_TYPE |\
                                                    kShortExternalStringTag |\
                                                    kInternalizedTag,
            'SHORT_EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE':\
                EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE | kShortExternalStringTag |\
                kInternalizedTag,
            'SHORT_EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE':\
                EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE |\
                kShortExternalStringTag | kInternalizedTag,
            'STRING_TYPE': INTERNALIZED_STRING_TYPE | kNotInternalizedTag,
            'ONE_BYTE_STRING_TYPE':\
                ONE_BYTE_INTERNALIZED_STRING_TYPE | kNotInternalizedTag,
            'CONS_STRING_TYPE': kTwoByteStringTag | kConsStringTag | kNotInternalizedTag,
            'CONS_ONE_BYTE_STRING_TYPE':\
                kOneByteStringTag | kConsStringTag | kNotInternalizedTag,
            'SLICED_STRING_TYPE':\
                kTwoByteStringTag | kSlicedStringTag | kNotInternalizedTag,
            'SLICED_ONE_BYTE_STRING_TYPE':\
                kOneByteStringTag | kSlicedStringTag | kNotInternalizedTag,
            'EXTERNAL_STRING_TYPE':\
                EXTERNAL_INTERNALIZED_STRING_TYPE | kNotInternalizedTag,
            'EXTERNAL_ONE_BYTE_STRING_TYPE':\
                EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE | kNotInternalizedTag,
            'EXTERNAL_STRING_WITH_ONE_BYTE_DATA_TYPE':\
                EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE |\
                kNotInternalizedTag,
            'SHORT_EXTERNAL_STRING_TYPE':\
                SHORT_EXTERNAL_INTERNALIZED_STRING_TYPE | kNotInternalizedTag,
            'SHORT_EXTERNAL_ONE_BYTE_STRING_TYPE':\
                SHORT_EXTERNAL_ONE_BYTE_INTERNALIZED_STRING_TYPE | kNotInternalizedTag,
            'SHORT_EXTERNAL_STRING_WITH_ONE_BYTE_DATA_TYPE':\
                SHORT_EXTERNAL_INTERNALIZED_STRING_WITH_ONE_BYTE_DATA_TYPE |\
                kNotInternalizedTag,
            'THIN_STRING_TYPE': kTwoByteStringTag | kThinStringTag | kNotInternalizedTag,
            'THIN_ONE_BYTE_STRING_TYPE':\
                kOneByteStringTag | kThinStringTag | kNotInternalizedTag
        }

def get_v8_map_dict():
    fpath = '/home/z/Projects/open/v8/v8/src/objects.h'
    analyzer = V8Analyzer(fpath)
    return analyzer.process()

def get_jsc_js_type_dict():
    fpath = '/home/z/Projects/open/safari-604-branch/Source/JavaScriptCore/runtime/JSType.h'
    analyzer = JSCAnalyzer(fpath)
    return analyzer.process()

if __name__ == '__main__':
    fpath = '/home/z/Projects/open/v8/v8/src/objects.h'
    analyzer = V8Analyzer(fpath)
    x = analyzer.process()
    #print(x)
    for (k, v) in x.items():
        print('{}: {}'.format(k, v))
