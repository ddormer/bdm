module.exports = function(grunt) {
  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: 'bdm/static/javascript/<%= pkg.name %>.js',
        dest: 'bdm/static/javascript/<%= pkg.name %>.min.js'
      }
    },
    bowercopy: {
      options: {
        clean: true,
        srcPrefix: 'bower_components'
      },
      javascript: {
        options: {
          destPrefix: '<%= pkg.name %>/static/javascript/'
        },
          files: {
            'jquery/jquery.min.js': 'jquery/dist/jquery.min.js',
            'react/react.min.js': 'react/react.min.js'
          }
      },
      css: {
        options: {
          destPrefix: '<%= pkg.name %>/static/css/'
        },
          files: {
            'fontawesome/css/': 'fontawesome/css/',
            'fontawesome/fonts/': 'fontawesome/fonts/',
            'pure/pure-min.css': 'pure/pure-min.css',
            'pure/grids-responsive-min.css': 'pure/grids-responsive-min.css'
          }
      }
   }
  });

  grunt.loadNpmTasks('grunt-bowercopy');
  grunt.loadNpmTasks('grunt-contrib-uglify');

  // Default task(s).
  grunt.registerTask('default', ['uglify', 'bowercopy']);
};
