<template>

  <td :class="cellData['class'] ? cellData['class'] : null">

    <!-- Sorting key -->
    <span v-if="cellData['sort']" class="hidden">
      {{ cellData["sort"] }}
    </span>
    <!-- Icons or Emoji -->
    <span v-if="cellData['icon']" class="glyphicon" :class="cellData['icon']">
    </span>
    <span v-if="cellData['emoji']" class="emoji" >
      {{ cellData["emoji"] }}
    </span>

    <!-- Tooltip/Popovers Hovers Wrapper -->
    <span
      :title="cellData['tooltip']"
      :data-toggle="cellData['popover'] || cellData['tooltip'] ? 'tooltip' : ''"
      v-on:mouseover="checkForPopover">

      <!-- Links and modals -->
      <span v-if="cellData['link'] || cellData['modal']">
        <a v-if="cellData['link']" :href="cellData['link']" >
          <span v-html="cellData['text']"></span>
        </a>
        <a v-if="cellData['modal']" :data-target="cellData['modal']" >
          <span v-html="cellData['text']"></span>
        </a>
      </span>
      <span v-else>
        <span v-html="cellData['text']"></span>
      </span>

    </span>

    <span v-if="cellData['subtext']">
      <br><span class="small" v-html="cellData['subtext']"></span>
    </span>

    <div class="popover-raw hide" v-if="cellData['popover']">
      <li v-if="popContent['text']"
          v-on:click=""
          v-for="popContent in cellData['popover']['content']" class="list-group-item">
        <a v-if="popContent['link']" :href="popContent['link']">
          {{{ popContent['text'] }}}
        </a>
        <span v-else>
          {{{ popContent['text'] }}}
        </span>
      </li>
    </div>

  </td>

</template>

<script>
import PopoverMixin from '../mixins/PopoverMixin.vue'

export default {
  mixins: [PopoverMixin],
  props: {
    cellData: Object,
  },
  methods: {
    getPopOverTitle: function() {
      return this.cellData['popover']['title'];
    },
    checkForPopover: function(event) {
      // Need to check the data exists for a popover before constructing it
      if (typeof this.cellData['popover'] !== 'undefined') {
        this.setupPopover(event);
      }
    },
    emitSignal: function(signalName, signalData) {
      this.$dispatch(signalName, signalData)
    }
  }
}
</script>
