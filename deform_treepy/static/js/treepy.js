
deserializers = {
   'create_mode': deserialize_tree_create,
   'selection_mode': deserialize_tree_selection
}

serializers = {
    'create_mode': serialize_tree_create,
    'selection_mode': serialize_tree_selection
}


function get_node_id(node){
  var obj = $(node.parents('li.jstree-node').children('a.jstree-anchor'));
  var parents = $.map(obj, function(el) { return $(el).text() }).reverse();
  return parents.join('-');
}

function init_keyword_values_tree(parent, tree_container, select_field, level){
     var level_data = $(tree_container.find(".keyword-data span[data-level=\'"+level+"']").first());
     var values = [];
     var can_create = 1;
     if (level_data.length > 0){
         // values = level_data.data('values').split(',');
         var parent_key = get_node_id(parent);
         var tree = level_data.data('values');
         if(parent_key in tree){
            values = tree[parent_key]
          }

         can_create = parseInt(level_data.data('can-create'));
     };

     if (can_create == 0){
        select_field.select2({containerCssClass: 'form-control'})
     };
     $(tree_container.find('.select2.select2-container')).css('width', '152px');
     for (i=0; i<values.length; i++){
     	if($(select_field).find("option[value=\""+values[i]+"\"]").length == 0){
            select_field.append("<option value=\""+values[i]+"\">"+values[i]+"</option>");
        };
     };
};

function edit(inst, obj, default_text) {
	    var old_value = obj.text;
         obj = inst.get_node(obj);
         var level = inst.get_path(obj).length-2;
         if(!obj) { return false; }
         if(inst.settings.core.check_callback === false) {
            inst._data.core.last_error = { 'error' : 'check',
                                           'plugin' : 'core',
                                           'id' : 'core_07',
                                           'reason' : 'Could not edit node because of check_callback' };
            inst.settings.core.error.call(inst, inst._data.core.last_error);
            return false;
         }
         default_text = typeof default_text === 'string' ? default_text : obj.text;
         inst.set_text(obj, "");
         obj = inst._open_to(obj);
         var rtl = inst._data.core.rtl,
            w  = inst.element.width(),
            a  = obj.children('.jstree-anchor'),
            s  = $('<span>'),
            t  = default_text,
            h1 = $("<"+"div />", { css : { "position" : "absolute", "top" : "-200px", "left" : (rtl ? "0px" : "-1000px"), "visibility" : "hidden" } }).appendTo("body"),
            h2 = $("<"+"select />", {
                  "value" : t,
                  "class" : "jstree-rename-input",
                  "css" : {
                     "padding" : "0",
                     "border" : "1px solid silver",
                     "box-sizing" : "border-box",
                     "display" : "inline-block",
                     "height" : (inst._data.core.li_height) + "px",
                     "lineHeight" : (inst._data.core.li_height) + "px",
                     "width" : "150px"
                  },
                  "change" : $.proxy(function () {
			                     var i = s.children(".jstree-rename-input"),
			                         v = i.val(),
                               new_v = v;
                          if(v === ""){v = t};
			                     h1.remove();
			                     s.replaceWith(a);
			                     s.remove();
			                     selected_value = t;
			                     inst.set_text(obj, t);
			                     if(new_v === undefined || new_v === "" || inst.rename_node(obj, $('<div></div>').text(v)[inst.settings.core.force_text ? 'text' : 'html']()) === false) {
			                          inst.delete_node(obj)
			                       };

			                      var target_id = $(inst.element.parents('.tree-container').find('.keyword-data').first()).data('target');
                            var new_value = deserializers.create_mode(inst.get_json());
                            var target = $('input[id^="'+target_id+'"]')
			                      target.attr('value', new_value);
                            target.trigger('change')
                   			}, inst),
               }),
            fn = {
                  fontFamily     : a.css('fontFamily')      || '',
                  fontSize    : a.css('fontSize')        || '',
                  fontWeight     : a.css('fontWeight')      || '',
                  fontStyle      : a.css('fontStyle')    || '',
                  fontStretch    : a.css('fontStretch')     || '',
                  fontVariant    : a.css('fontVariant')     || '',
                  letterSpacing  : a.css('letterSpacing')   || '',
                  wordSpacing    : a.css('wordSpacing')     || ''
            };
         s.attr('class', a.attr('class')).append(a.contents().clone()).append(h2);
         a.replaceWith(s);
         h1.css(fn);
         $(h2.css(fn).width(150)[0]).select();
         var select_text = treepy_translate('- Select -');
         $(h2).append("<option value=\'\'>"+select_text+"</option>");
         if (!old_value.match("New node.*")){
         	if ($(h2).find("option[value=\""+old_value+"\" ]").length == 0){
                $(h2).append("<option value=\""+old_value+"\">"+old_value+"</option>");
            };
            $($(h2).find("option[value=\""+old_value+"\"]")).attr('selected', 'selected');
         };
         $(h2).select2({tokenSeparators: [","],
               containerCssClass: 'form-control',
               tags: true});

         init_keyword_values_tree($(obj.parents('.jstree-node').first().find('.jstree-anchor').first()),
                                  $($(h2).parents('.tree-container').first()),
                                  $(h2),
                                  level);
         var select_container = $($($(h2).parents('.jstree-anchor').first()).find('.select2.select2-container'));
         select_container.css('display', 'inline-block');
         $(h2).select2("open");
         select_container.click(function(event){
    			event.stopPropagation();
		  });
};


function serialize_node(node_name, node_children, type){
  var children = [];
  for(n in node_children){
        children.push(serialize_node(n, node_children[n], 'default'))
  };
    var result = {"text": node_name, "type": type, "children":children, 'state' : {
           'opened' : true
         }};
    return result
}

//node : {"node_name": [subnodes]}
function serialize_tree_create(tree_string){
  var tree = {};
  try {
      tree = JSON.parse(tree_string);
  }
  catch(err) {
      return [];
  };
  var children = [];
  for(n in tree){
      children.push(serialize_node(n, tree[n], 'root'))
  };
  return children
};

//************************************* serialize_diff *****************************

function get_diff_node(node_name, subnode, subtree, diff_marker){
   var diff_node = {is_diff: false, subtree: {}}
   for(var i in subtree){
    if(i == node_name+diff_marker){
      diff_node.is_diff = true;
      diff_node.subtree = subtree[node_name+diff_marker]
    } else if(i == node_name){
      diff_node.subtree = subtree[node_name]
    };
   };

  return diff_node
}

function serialize_node_diff(node_name, node_children, type, is_diff, diff_tree, diff_marker){
  var children = [];
  for(var n in node_children){
        var diff_node = get_diff_node(n, node_children[n], diff_tree, diff_marker);
        children.push(serialize_node_diff(n, node_children[n], 'default',
                     diff_node.is_diff, diff_node.subtree, diff_marker))
  };
  var result = {"text": node_name, "type": type, "children":children};
  if (is_diff){
    result.state = {
        checked  : true,
        opened : true
       };
    result['type'] = "new_default";
  }else{
    result.state = {
         opened : true
       };
  }
  return result
}

function serialize_tree_diff(tree_string, diff_tree_str, diff_marker){
  var tree = {};
  try {
      tree = JSON.parse(tree_string);
  }
  catch(err) {
      return [];
  };

  var diff_tree = {};
  try {
      diff_tree = JSON.parse(diff_tree_str);
  }
  catch(err) {
      diff_tree = {};
  };

  var children = [];
  for(var start_n in tree){
      var diff_node = get_diff_node(start_n, tree[start_n], diff_tree, diff_marker);
      children.push(serialize_node_diff(start_n, tree[start_n], 'root',
                    diff_node.is_diff, diff_node.subtree, diff_marker))
  };
  return children
};

//***************************************** serilize ****************************************

function get_selected_node(node_name, subnode, subtree){
   var selected = {is_selected: false, subtree: {}}
   for(var i in subtree){
    if(node_name == i){
      selected.is_selected = true;
      selected.subtree = subtree[node_name]
    };
   };

  return selected
}

function serialize_node_selection(node_name, node_children, type, is_selected, selection_tree){
  var children = [];
  for(var n in node_children){
        var selected = get_selected_node(n, node_children[n], selection_tree);
        children.push(serialize_node_selection(n, node_children[n], 'default',
                     selected.is_selected, selected.subtree))
  };
  var result = {"text": node_name, "type": type, "children":children};
  var selection_len = Object.keys(selection_tree).length;
  if ((children.length == 0 || selection_len == 0 || children.length == selection_len) && is_selected){
    result.state = {
        checked  : true,
        opened : true
       };
  } else if (is_selected){
    result.state = {
         opened : true
       };
  }
  return result
}

function serialize_tree_selection(tree_string, selection_tree_str){
  var tree = {};
  try {
      tree = JSON.parse(tree_string);
  }
  catch(err) {
      return [];
  };

  var selection_tree = {};
  try {
      selection_tree = JSON.parse(selection_tree_str);
  }
  catch(err) {
      selection_tree = {};
  };

  var children = [];
  for(var start_n in tree){
      var selected = get_selected_node(start_n, tree[start_n], selection_tree);
      children.push(serialize_node_selection(start_n, tree[start_n], 'root',
                    selected.is_selected, selected.subtree))
  };
  return children
};


function deserialize_node(node){
  var children = [],
      node_name = node.text;
  for(subnode in node.children){
        children.push(deserialize_node(node.children[subnode]))
  };
    var result = '\"'+node_name+'\": {'+children.join(',')+'}';
    return result
}


function deserialize_tree_create(objects){
	var children = [];
	for(start_n in objects){
        children.push(deserialize_node(objects[start_n]))
	};
   return '{'+children.join(',')+'}'
};


function deserialize_node_selection(node, tree_tag){
  var children = [],
      node_name = node.text;
  for(subnode in node.children){
        var object = node.children[subnode];
        var is_selected = $(tree_tag).find('#'+object.id+' a.jstree-checked').length > 0 || object.state.checked;
        if (is_selected){
          children.push(deserialize_node_selection(object, tree_tag))
        }
  };
    var result = '\"'+node_name+'\": {'+children.join(',')+'}';
    return result
}

function deserialize_tree_selection(objects, tree_tag){
  var children = [];
  for(start_n in objects){
        var object = objects[start_n];
        var is_selected = $(tree_tag).find('#'+object.id+' a.jstree-checked').length > 0 || object.state.checked;
        if (is_selected){
            children.push(deserialize_node_selection(object, tree_tag))
        }
  };
   return '{'+children.join(',')+'}'
};


function create_tree(oid){
	  var default_keywords_field = $('#'+oid);
    var default_keywords = default_keywords_field.val();
    var input_tree = serializers.create_mode(default_keywords);
    var keywords_tree = input_tree;
    var source_tree = default_keywords_field.data('source_tree');
    var is_source = false;
    if(source_tree != ""){
      keywords_tree = serializers.selection_mode(JSON.stringify(source_tree), default_keywords);
      is_source = true
    }
    var target = $('#jstree-'+oid);
    var max_len = parseInt($($(target.parents('.tree-container').first()).find('.keyword-data').first()).data('max-len'))+1;
    var plugins = [
     "search", "types", "wholerow",  "unique"
    ];
    if (is_source){
      plugins.push('checkbox');

    }else{
      plugins.push("contextmenu")
    };
    target.jstree({
    'core' : {
      "animation" : 0,
      "check_callback" : true,
      'data' : keywords_tree

    },
    checkbox : {
        tie_selection : false
     },
   'contextmenu' : {
      'items' : function(node) {
         $('.jstree-anchor select').trigger("change");
         var tmp = $.jstree.defaults.contextmenu.items();
         delete tmp.create.action;
         delete tmp.ccp;
         tmp.create.label = treepy_translate("Add a category");
         tmp.create.action = function (data) {
                   var inst = $.jstree.reference(data.reference),
                       obj = inst.get_node(data.reference);
                   inst.create_node(obj, { type : "default" }, "last", function (new_node) {
                             setTimeout(function () { edit(inst, new_node); },0);
                        });
               };
         tmp.rename.action = function (data) {
                  var inst = $.jstree.reference(data.reference),
                      obj = inst.get_node(data.reference);
                  edit(inst, obj);
               };
         tmp.rename.label = treepy_translate("Rename");
         tmp.remove.label = treepy_translate("Remove");
         if(this.get_type(node) === "default"){
         	var inst = $.jstree.reference(node),
         	    obj = inst.get_node(node);
            var level = inst.get_path(obj).length;
            if (max_len <= level){
            	delete tmp.create
            }
         };
         if(this.get_type(node) === "root") {
            delete tmp.rename;
            delete tmp.remove;
         };
         return tmp;
      }
   },

    "types" : {
          "#" : {
            "max_children" : 1,
            "max_depth" : max_len,
            "valid_children" : ["root"]
          },
          "root" : {
            "icon" : "glyphicon glyphicon-folder-open",
            "valid_children" : ["default"]
          },
          "default" : {
            "icon" : "glyphicon glyphicon-tag",
            "valid_children" : ["default"]
          },
  },
  "plugins" : plugins
  }).on('delete_node.jstree', function(){
        var inst = $.jstree.reference($(this));
        var new_value = deserializers.create_mode(inst.get_json());
        var target_id = $(inst.element.parents('.tree-container').find('.keyword-data').first()).data('target');
        var target = $('input[id^="'+target_id+'"]')
        target.attr('value', new_value);
        target.trigger('change')

  }).on('check_node.jstree uncheck_node.jstree', function(e, data){
        var inst = $.jstree.reference($(this));
        var new_value = deserializers.selection_mode(inst.get_json(), $(this));
        var target_id = $(inst.element.parents('.tree-container').find('.keyword-data').first()).data('target');
        var target = $('input[id^="'+target_id+'"]')
        target.attr('value', new_value);
        target.trigger('change')
  });
};

function get_invalid_nodes(){
	var result = [];
	var nodes = $('li.jstree-node.jstree-leaf');
    for (i=0; i<nodes.length; i++){
    	var anchor = $($(nodes[i]).find('a.jstree-anchor').first());
    	if(anchor.length == 0 || anchor.text() == ''){
    		result.push($(nodes[i]))
    	}
    }
    return result
};

function remove_all_invalid_nodes(){
	var nodes_to_del = get_invalid_nodes();
    for (i=0; i<nodes_to_del.length; i++){
    	var node = $(nodes_to_del[i]);
    	var anchor = $(node.find('a.jstree-anchor').first());
    	if(anchor.length == 0 || anchor.text() == ''){
    		var inst = $.jstree.reference($(node.parents('div.tree').first()));
    		inst.delete_node({id: node.attr('id')})
    	}
    }
}
function read_tree(tree){
    var default_keywords = tree.data('source_tree');
    var is_diff = tree.data('is_diff');
    if(is_diff){
      var diff_marker = tree.data('diff_marker');
      var diff_keywords = tree.data('diff_tree');
      var input_tree = serialize_tree_diff(
        JSON.stringify(default_keywords), JSON.stringify(diff_keywords), diff_marker); 
    }else{
        var input_tree = serialize_tree_create(JSON.stringify(default_keywords));
    }
    var keywords_tree = input_tree;
    var plugins = [
     "search", "types", "wholerow",  "unique"
    ];
    
    tree.jstree({
    'core' : {
      "animation" : 0,
      "check_callback" : true,
      'data' : keywords_tree

    },
    "types" : {
          "#" : {
            "max_children" : 1,
            "valid_children" : ["root"]
          },
          "root" : {
            "icon" : "glyphicon glyphicon-folder-open",
            "valid_children" : ["default", "new_default"]
          },
          "default" : {
            "icon" : "glyphicon glyphicon-tag",
            "valid_children" : ["default", "new_default"]
          },
          "new_default" : {
            "icon" : "glyphicon glyphicon-plus-sign diff-tree-node",
            "valid_children" : ["default", "new_default"]
          }
  },
  "plugins" : plugins
  })
}

function read_trees(source){
  var trees = $('.read-tree');
  if(source != undefined){
    trees = $(source).find('.read-tree')
  }
  for (i=0; i<trees.length; i++){
    var tree = $(trees[i]);
    read_tree(tree)
  };

};

$(document).ready(function(){
  read_trees();
	 $(document).click(function(event){
	 	if($(event.target).find(".vakata-contextmenu-sep").length === 0){
	 	    $('.jstree-anchor select').trigger("change");
	 	};

	 });

});

$(document).on('click', 'a.jstree-anchor', function(event){
      $(this).contextmenu()
})