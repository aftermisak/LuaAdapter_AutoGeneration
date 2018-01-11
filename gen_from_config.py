#coding=utf8

import sys
import json

codes_fmt = '''
	auto ns = LuaAdapterEnvironment::getInstance().getNamespace("%s");
	ns->begin();
	{
		ns->registerClass("%s", typeid(%s));
		auto cls = ns->getClass("%s");
		cls->begin();
		%s//extends
		%s//constructors
		%s//destructor
		%s//nonmember variables
		%s//member variables
		%s//nonmember functions
		%s//member functions
		cls->end();
	}
	ns->end();
'''

def __gen_extends( cls_full_name, super_clses_full ):
	if len(super_clses_full) == 0:
		return ""
	return 'cls->extends<%s, %s>();\n' %( cls_full_name, ",".join( super_clses_full ) )

def __gen_nonmember_function( cls_full_name, func_name ):
	return 'cls->registerFunction(%s, "%s")\n' % ( "::".join((cls_full_name, func_name)), func_name )

def __gen_member_function( cls_full_name, func_name ):
	return 'cls->registerFunction(&%s, "%s")\n' % ( "::".join((cls_full_name, func_name)), func_name )

def __gen_nonmember_variable( cls_full_name, vari_name ):
	return 'cls->registerVariable(&%s, "%s")\n' % ( "::".join((cls_full_name, vari_name)), vari_name )

def __gen_member_variable( cls_full_name, vari_name ):
	return __gen_nonmember_variables( cls_full_name, vari_name )




def gen_cls_codes( ns_name, cls_full_name, super_clses_full, nonmember_funcs, member_funcs, nonmember_varis, member_varis ):
	la_ns_name = ns_name.replace( "::", "." )
	la_cls_full_name = cls_full_name.replace( "::", "." )

	codes_list = []
	codes_list.append( 'auto ns = LuaAdapterEnvironment::getInstance().getNamespace("%s");\n' % la_ns_name )
	codes_list.append( 'ns->begin();{\n' );
	codes_list.append( '    ns->registerClass("%s", typeid(%s));\n' % (la_cls_full_name, cls_full_name) );
	codes_list.append( '    auto cls = ns->getClass("%s");\n' % la_cls_full_name );
	codes_list.append( '    cls->begin();\n' );
	codes_list.append( '    %s' % __gen_extends( cls_full_name, super_clses_full ) )
	
	for vari_name in nonmember_varis:
		codes_list.append( '    %s' % __gen_nonmember_variable( cls_full_name, vari_name ) )

	for vari_name in member_varis:
		codes_list.append( '    %s' % __gen_member_variable( cls_full_name, vari_name ) )

	for func_name in nonmember_funcs:
		codes_list.append( '    %s' % __gen_nonmember_function( cls_full_name, func_name) )

	for func_name in member_funcs:
		codes_list.append( '    %s' % __gen_member_function( cls_full_name, func_name) )

	codes_list.append( '    cls->end();\n' );
	codes_list.append( '}ns->end();\n' );

	return codes_list

def __read_file_content( fpath ):
    f = open( fpath )
    if not f:
        raise "cant open file %s" % atlas
    fContent = f.read()
    f.close()
    return fContent

def gen_by_config( fPath ):
	fContent = __read_file_content( fPath )
	fJson = json.loads( fContent )
	nsInfo = fJson["namespace"]
	ns_name = nsInfo["namespace_name"]
	for clsInfo in fJson["classes"]:
		cls_name = clsInfo["class_name"]
		cls_full_name = "::".join( [ns_name, cls_name] )
		super_clses = clsInfo.has_key("extends") and clsInfo["extends"] or ()

		def __path_ns( super_cls ):
			if super_cls.find( "::" ) == -1:
				return "::".join( [ns_name, super_cls] )
			else:
				return super_cls

		super_clses_full = map( __path_ns, super_clses )

		nonmember_funcs = clsInfo.has_key("nonmember_functions") and clsInfo["nonmember_functions"] or ()
		member_funcs = clsInfo.has_key("member_functions") and clsInfo["member_functions"] or ()

		nonmember_varis = clsInfo.has_key("nonmember_variables") and clsInfo["nonmember_variables"] or ()
		member_varis = clsInfo.has_key("member_variables") and clsInfo["member_variables"] or ()

		codes_list = gen_cls_codes( ns_name, cls_full_name, super_clses_full, 
		  nonmember_funcs, member_funcs, nonmember_varis, member_varis )
		for code in codes_list:
			print( code )


if "__main__" == __name__:
	fPath = sys.argv[1]
	gen_by_config(fPath)